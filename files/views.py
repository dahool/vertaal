import re
import pygments
import pygments.lexers
import pygments.formatters
import traceback
import os
import thread
import time
    
from django.utils.translation import ungettext, ugettext as _
from django.utils.encoding import smart_unicode
from django.shortcuts import render_to_response, get_object_or_404
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.template import RequestContext, loader, Context
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string
from django.contrib.auth.models import User
from common.decorators import permission_required_with_403
from common.middleware.exceptions import Http403
from common.simplexml import XMLResponse
from django.db.models import Q
from components.models import *
from releases.models import *
from languages.models import *
from teams.models import *
from files.models import *
from versioncontrol.forms import *
from files.forms import *
from versioncontrol.models import *
from versioncontrol.manager import *
import files.lib.handlers as filehandler
from files.lib.handlers import handle_uploaded_file, handle_text_file
from app.log import (logger)
from django.conf import settings
from common.view.decorators import render
import StringIO
from django.core.cache import cache

from django.shortcuts import redirect

from deferredsubmit import handler as deferredhandler

from django.contrib import messages
from djangopm.utils import send_pm

try:
    import hashlib
    hash = hashlib.sha1
except ImportError:
    import sha
    hash = sha.new
    
from common.cache.file import FileCache

from files.lib.diff_match_patch import diff_match_patch

def escape(text):
    return text.replace("<", "&lt;").replace(">","&gt;")

def check_status(fn):
    """check if the project is enabled"""
    def status_fn(self, *args, **kw):
        request = kw.get('request')
        if kw.has_key('release'):
            release = get_object_or_404(Release,slug=kw['release'])
        elif kw.has_key('slug'):
            pofile = get_object_or_404(POFile,slug=kw['slug'])
            release = pofile.release
        else:
            raise Http404
        if not release.enabled or not release.project.enabled:
            if release.project.is_maintainer(self.user):
                if not release.project.enabled:
                    messages.warning(request, _("This project is disabled. You shouldn't change anything here."))
                else:
                    messages.warning(request, _("This release is disabled. You shouldn't change anything here."))
            else:
                raise Http403
        return fn(self, *args, **kw)
    return status_fn 

@login_required
@check_status
def upload(request, release, language):
    res = {}
    if request.method == "POST":
        res['back'] = reverse('list_files',
                             kwargs={ 'release': release,
                                      'language': language})
        r = get_object_or_404(Release, slug=release)
        l = get_object_or_404(Language, code=language)
        form = UploadFileForm(request.POST, request.FILES)
        res['form'] = form
        if form.is_valid():
            try:
                logger.debug(request.FILES)
                # first we add the files to the queue
                submits = handle_uploaded_file(request.FILES['file'], r, l, request.user, form.cleaned_data['comment'])
                # then we check if it is possible to commit now
                team = Team.objects.get(project=r.project,language=l)
                if r.project.repo_user and team.submittype == 1 and team.can_commit(request.user):
                    do_commit(request, submits, request.user, r.project.repo_user, r.project.get_repo_pwd())
                else:
                    #thread.start_new_thread(create_diff_cache, (submits,))
                    messages.info(request, _("Your file was uploaded and added to the submission queue."))
            except Exception, e:
                logger.error(e)
                res['message']=e.message.split("$$")
                return render_to_response('files/upload_failed.html',
                                          res,
                                          context_instance = RequestContext(request))
        res.update(get_file_list(request, None, release, language))
    else:
        raise Http403
    return render_to_response('files/file_list.html',
                              res,
                              context_instance = RequestContext(request))    

@login_required
def toggle(request, slug):
    res = {}
    if request.method == "POST":
        try:
            file = POFile.objects.get(slug=slug)
        except:
            return XMLResponse({'message': _('File not found.')})
        else:
            if not file.release.enabled or not file.release.project.enabled:
                return XMLResponse({'message': _('Sorry, you are not supposed to change anything on a disabled component.')})
            
            team = Team.objects.get(project=file.component.project, language=file.language)
            if not team.is_member(request.user):
                return XMLResponse({'message': _('You are not a member of this team.')})
                
            res['id'] = file.slug
            if file.locked:
                # if the file is locked by the same user or the user is admin or coord
                # then can unlock the file
                if file.locks.get().can_unlock(request.user):
                    if file.submits.all_pending():
                        res['message'] = _('The file will be unlocked once submitted.')       
                    else:
                        file.locks.get().delete()
                        if request.POST.has_key('text'):
                            comment = request.POST.get('text')
                        else:
                            comment = ''
                        POFileLog.objects.create(pofile=file, user=request.user, action='R', comment=comment)
                else:
                    res['message'] = _('This file is already locked by someone else.')
            else:
                #lock = POFileLock.objects.create(pofile=file, owner=request.user)
                file.locks.create(owner=request.user)
                #file.locks.add(lock)
        page = render_to_string('files/file_list_row.html',
                                {'file': file, 'team': team},
                                context_instance = RequestContext(request))
        res['content_HTML'] = page
        return XMLResponse(res)
    else:
        raise Http403

@login_required
def toggle_assigned(request, slug, translator=False, remove=False):
    res = {}
    if request.method == "POST":
        try:
            file = POFile.objects.get(slug=slug)
        except:
            return XMLResponse({'message': _('File not found.')})
        
        if not file.release.enabled or not file.release.project.enabled:
            return XMLResponse({'message': _('Sorry, you are not supposed to change anything on a disabled component.')})

        team = Team.objects.get(project=file.component.project, language=file.language)
        if not team.is_member(request.user) and not request.user.is_superuser:
            return XMLResponse({'message': _('You are not a member of this team.')})
        can_manage = team.can_manage(request.user)
        
        res['id'] = file.slug
        cmt = ''
        act = None
        if remove:
            if file.assigns.all():
                assign = file.assigns.get()
            if assign:
                if translator:
                    auser = assign.translate
                    if auser:
                        if can_manage or auser == request.user:
                            if file.submits.all_pending() and file.submits.get_pending().owner == auser:
                                return XMLResponse({'message': _('The file has a pending submit. Cannot be released right now.')})
                            else:
                                assign.translate = None
                                if auser != request.user:
                                    cmt = _('Removed %s') % auser.username
                                act=LOG_ACTION['RE_TRA']
                        else:
                            return XMLResponse({'message': _('You are not authorized to perform this action.')})                        
                else:
                    auser = assign.review
                    if auser:
                        if can_manage or auser == request.user:
                            if file.submits.all_pending() and file.submits.get_pending().owner == auser:
                                return XMLResponse({'message': _('The file has a pending submit. Cannot be released right now.')})
                            else:
                                assign.review = None
                                if auser != request.user:
                                    cmt = _('Removed %s') % auser.username                            
                                act=LOG_ACTION['RE_REV']
                        else:
                            return XMLResponse({'message': _('You are not authorized to perform this action.')})
                if file.locked:
                    if file.locks.get().owner == auser:
                        file.locks.get().delete()
                        POFileLog.objects.create(pofile=file, user=request.user, action=LOG_ACTION['ACT_LOCK_DEL'])
                if act:
                    log = POFileLog.objects.create(pofile=file, user=request.user, action=act, comment=cmt)                        
                    assign.save()
        else:
            if request.POST.has_key('userid'):
                userid = request.POST.get('userid')
            else:
                userid = None
            if file.assigns.all():
                assign = file.assigns.get()
            else:
                #assign = file.assigns.create()
                assign = POFileAssign(pofile=file)
            if translator:
                if assign.translate:
                    return XMLResponse({'message': _('This file already has an assigned translator.')})
                
                if not can_manage or not userid:
                    assign.translate = request.user 
                else:
                    assign.translate = User.objects.get(id=userid)
                    if assign.translate != request.user:
                        send_pm(assign.translate, _('File assigned'), _('You had been designated as translator of %(file)s') % {'file': smart_unicode(file)})
                if assign.translate != request.user:
                    cmt = _('Assigned to %s') % assign.translate.username                
                act=LOG_ACTION['AS_TRA']
                    
            else:
                if assign.review:
                    return XMLResponse({'message': _('This file already has an assigned reviewer.')})
                
                if not can_manage or not userid:
                    assign.review = request.user 
                else:
                    assign.review = User.objects.get(id=userid)
                    if assign.review != request.user:
                        send_pm(assign.review, _('File assigned'), _('You had been designated as reviewer of %(file)s') % {'file':smart_unicode(file)})

                if assign.review != request.user:
                    cmt = _('Assigned to %s') % assign.review.username                
                act=LOG_ACTION['AS_REV']
                
            if assign.translate == assign.review:
                return XMLResponse({'message': _('Sorry, the translator and the reviewer cannot be the same user.')})
            
            POFileLog.objects.create(pofile=file, user=request.user, action=act, comment=cmt)
            assign.save()
            
        page = render_to_string('files/file_list_row.html',
                                {'file': file, 'team': team},
                                context_instance = RequestContext(request))
        res['content_HTML'] = page
        return XMLResponse(res)
    else:
        raise Http403
        
@login_required
def toggle_mark(request, slug):
    res = {}
    if request.method == "POST":
        try:
            file = POFile.objects.get(slug=slug)
        except:
            return XMLResponse({'message': _('File not found.')})
        
        if not file.release.enabled or not file.release.project.enabled:
            return XMLResponse({'message': _('Sorry, you are not supposed to change anything on a disabled component.')})

        team = Team.objects.get(project=file.component.project, language=file.language)
        if not team.is_member(request.user):
            return XMLResponse({'message': _('You are not a member of this team.')})
            
        res['id'] = file.slug
        if file.assigns.all():
            assign = file.assigns.get()
        else:
            assign = False
        if (team.can_manage(request.user) or
            (assign and (assign.translate==request.user or assign.review==request.user))):
            # to avoid mark collision
            current_mark = request.POST.get('mark')
            if int(current_mark) == file.status:
                st = None
                if file.status == 0:
                    file.status = 1
                    st = 'ST_TRAN'
                elif file.status == 1:
                    file.status = 2
                    st = 'ST_REV'
                elif file.status == 2:
                    file.status = 3
                    st = 'ST_COMPL'
                if st:
                    file.save()
                    file.log.create(action=LOG_ACTION[st],user=request.user)
                    
                    if file.status == 1:
                        if assign and assign.review:
                            set_user_language(assign.review)
                            send_pm(assign.review, subject=_("File %s ready for review.") % smart_unicode(file))                    
        else:
            return XMLResponse({'message': _('You are not authorized to perform this action.')})

        page = render_to_string('files/file_list_row.html',
                                {'file': file, 'team': team},
                                context_instance = RequestContext(request))
        res['content_HTML'] = page
        return XMLResponse(res)
    else:
        raise Http403
    
def get_file_list(request, component=None, release=None, language=None):
    q = POFile.objects.filter()
    res = {}
    res['cookjar'] = {}
    if release:
        r = res['release'] = get_object_or_404(Release, slug=release)
        if r.read_only or r.project.read_only:
            if request.user.is_authenticated():
                messages.warning(request, _('This component is read only.'))
        q = q.filter(release=res['release'])
    if component:
        c = res['component'] = get_object_or_404(Component, slug=component)
        q = q.filter(component=res['component'])
    else:
        cook = 'cmpfilter_%s' % r.slug
        if request.POST.has_key('cmpfilter'):
            if request.POST.get('cmpfilter'):
                q = q.filter(component__in=request.POST.getlist('cmpfilter'))
                res['cfilter'] = [ int(i) for i in request.POST.getlist('cmpfilter') ]
        else:
            if cook in request.COOKIES:
                cf = request.COOKIES.get(cook).split(',')
                q = q.filter(component__in=cf)
                res['cfilter'] = [ int(i) for i in cf ]
            else:
                co = r.project.components.all()[0]
                q = q.filter(component=co)
                res['cfilter'] = [int(co.pk)]
        #filter_data = ",".join([ str(i) for i in res['cfilter']])
        #res['cookjar'][cook] = filter_data
    if language:
        l = res['language'] = get_object_or_404(Language, code=language)
        q = q.filter(language=res['language'])
        if r:
            res['team'] = get_object_or_404(Team, language=l,project=r.project)
            #res['team'] = Team.objects.get(language=l,project=r.project)

    if request.user.is_authenticated():
        cook = 'shide_%s' % r.slug
        if request.POST.has_key('hideTranslated'):
            if request.POST.get('hideTranslated')=='true':
                q = q.extra(where=['total>trans'])
                res['cookjar'][cook] = 'true'
                res['hideTranslated'] = 'true'
            else:
                res['cookjar'][cook] = None
        else:
            if cook in request.COOKIES:
                q = q.extra(where=['total>trans'])
                res['hideTranslated'] = 'true'
        
        cook = 'onlys_%s' % r.slug
        if request.POST.has_key('onlySelf'):
            if request.POST.get('onlySelf')=='true':
                q = q.filter(Q(assigns__translate__id=request.user.id) |
                             Q(assigns__review__id=request.user.id))
                res['cookjar'][cook] = 'true'
                res['onlySelf'] = 'true'
            else:
                res['cookjar'][cook] = None
        else:
            if cook in request.COOKIES:
                q = q.filter(Q(assigns__translate__id=request.user.id) |
                             Q(assigns__review__id=request.user.id))
                res['onlySelf'] = 'true'
                        
    res['file_list']=q
    res['last_actions'] = POFileLog.objects.last_actions(res['release'],10,res['language'])
    
    return res
    
@check_status
def list_files(request, component=None, release=None, language=None, filter = False):
    logger.debug('list_files %s - %s - %s ' % (component, release, language))
    
    res = get_file_list(request, component, release, language)
    
    cook = res.pop('cookjar',None)
    
    if filter:
        template = "files/file_list_table.html"
    else:
        template = "files/file_list.html"
    
    if request.GET.get('h', None):
        res['highlight'] = request.GET.get('h')
        logger.debug('highlight %s' % res['highlight'])
        if not component:
            try:
                p = POFile.objects.get(slug=request.GET.get('h'))
            except:
                pass
            else:
                res['default_component'] = p.component
        
    response = render_to_response(template,
                                   res,
                                   context_instance = RequestContext(request))
    
    if cook:
        for k,v in cook.iteritems():
            if v is None:
                response.delete_cookie(str(k))
            else:
                response.set_cookie(str(k), str(v), getattr(settings, 'COMMON_COOKIE_AGE', None))
    return response

def get_pot_file(request, slug):
    pofile = get_object_or_404(POFile, slug=slug)
    try:
        potfile = pofile.potfile.get()
    except:
        potfile = None
    if not potfile:
        logger.error("POTFile not found")
        raise Http404
    
    from files.external import get_external_url
    url = get_external_url(potfile)
    if url:
        logger.debug('Redirect to ' + url)
        response = redirect(url)
    else:
        try:
            content = potfile.handler.get_content()
        except Exception, e:
            logger.error(e)
            raise Http404            
        response = HttpResponse(content, mimetype='application/x-gettext; charset=UTF-8')
        attach = "attachment;"
        response['Content-Disposition'] = '%s filename=%s' % (attach, potfile.name)        
    return response


@login_required
def get_file_arch(request, id):
    sfile = get_object_or_404(POFileSubmit, pk=id)
    logger.debug("Get archived file %s" % id)
    from files.external import get_external_url
    url = get_external_url(sfile)
    if url:
        logger.debug('Redirect to ' + url)
        response = redirect(url)
    else:
        content = sfile.handler.get_content()
        response = HttpResponse(content, mimetype='application/x-gettext; charset=UTF-8')
        attach = "attachment;"
        response['Content-Disposition'] = '%s filename=%s' % (attach, sfile.filename)   
    return response

@login_required
def get_file(request, slug, view=False, submit=False):
    file = get_object_or_404(POFile, slug=slug)
    fileElement = file
    logger.debug("Get file - View: %s" % view)
    try:
        if submit:
            s = file.submits.get_pending()
            fileElement = s
            handler = s.handler
        else:
            handler = file.handler
    except Exception, e:
        logger.error(e)
        raise Http404
    if view:
        if submit:
            content = handler.get_content()
        else:
            content = handler.get_content(not view)
        if request.user.is_authenticated():
            ckey = 'v-%s-%s' % (request.user.username, slug)    
        else:
            ckey = 'v-#NON#-%s' % slug
        response = cache.get(ckey)
        if not response:
            lexer = pygments.lexers.GettextLexer()
            formatter = pygments.formatters.HtmlFormatter(linenos='inline')
            encre = re.compile(r'"?Content-Type:.+? charset=([\w_\-:\.]+)')
            m = encre.search(content)
            encoding = 'UTF-8'
            if m:
                encoding = m.group(1)
            text = content.decode(encoding)
            data = {'body': pygments.highlight(text, lexer, formatter),
                               'style': formatter.get_style_defs(),
                               'pofile': file,
                               'submit': submit,
                               'user': request.user,
                               'request': request,
                               'title': "%s: %s" % (file.component.name,
                                                    file.filename)}
            response = render_to_response('files/file_view.html',
                              data,
                              context_instance = RequestContext(request))
            cache.set(ckey, response)
        return response   
    else:
        from files.external import get_external_url
        url = get_external_url(fileElement)
        if url:
            logger.debug('Redirect to ' + url)
            response = redirect(url)        
        else:
            if submit:
                content = handler.get_content()
            else:
                content = handler.get_content(not view)            
            response = HttpResponse(content, mimetype='application/x-gettext; charset=UTF-8')
            attach = "attachment;"
            response['Content-Disposition'] = '%s filename=%s' % (attach, file.filename)        
    return response

@login_required
@check_status
def edit_file(request, slug):
    file = get_object_or_404(POFile, slug=slug)
    redirect = HttpResponseRedirect(reverse('list_files',
                            kwargs={'release': file.release.slug,
                              'language': file.language.code}))
    if request.method == 'POST':
        if request.POST.has_key('_save'):
            form = FileEditForm(request.POST)
            if form.is_valid():
                try:
                    handle_text_file(file, form.cleaned_data['content'], request.user, form.cleaned_data['comment'])
                    messages.info(request, message=_("Your file was added to the submission queue."))
                    return redirect
                except Exception, e:
                    res = str(e).split("$$")
                    for m in res:
                        messages.error(request, message=m[:-1])
                
        else:
            if file.submits.all_pending():
                s = file.submits.get_pending()
                s.enabled = True
                s.save()            
            return redirect
    else:
        if file.locked:
            if file.locks.get().owner.username != request.user.username:
                messages.warning(request, message=_("The file is locked by another user."))
                return redirect
        else:
            team = Team.objects.get(project=file.component.project, language=file.language)
            if not team.is_member(request.user):
                messages.warning(request, message=_("You are not a member of this team."))
                return redirect
            if file.assigns.all():
                assign = file.assigns.get()
                if not assign.translate == request.user and not assign.review == request.user:
                    messages.warning(request, message=_("You are not assigned to this file."))
                    return redirect                    
            else:
                messages.warning(request, message=_("You are not assigned to this file."))
                return redirect
            messages.info(request, message=_("The file is now locked on your name."))       
            POFileLock.objects.create(pofile=file, owner=request.user)
        try:
            if file.submits.all_pending():
                s = file.submits.get_pending()
                if s.locked:
                    messages.warning(request, message=_("This file is being processed. It can't be modified."))
                    return redirect                
                s.enabled = False
                s.save()
                content = s.handler.get_content()
                messages.info(request, message=_("You are editing the uploaded version of this file."))
                messages.info(request, message=_("The file was removed from the submission queue, remember to either save your work or cancel to put the file back in the queue."))
            else:
                content = file.handler.get_content(True)
        except:
            raise Http404
        form = FileEditForm(initial={'content': content})
        # end else
    return render_to_response("files/file_edit.html",
                               {'form': form,
                                'file': file,
                                'title': _('Editing %s') % file.filename},
                               context_instance = RequestContext(request))

def file_log(request, slug):
    file = get_object_or_404(POFile,slug=slug)
    return render_to_response("files/file_log.html",
                              {'pofile': file},
                              context_instance = RequestContext(request))
    
@login_required
def submit_team_file(request, team = None):

    if request.method != 'POST':
        raise Http403
    
    if team:
        t = get_object_or_404(Team, id=team)
        back = reverse('team_detail',
                       kwargs={'project': t.project.slug, 'lang': t.language.code})
    else:
        back = reverse('commit_queue')

    reject=False
    if request.POST.has_key('reject'):
        reject = True;

    files = []
    teams = set()
    for fid in request.POST.getlist('file'):
        try:
            sfile = POFileSubmit.objects.get(pk=fid)
            files.append(sfile)
            h = HasheableTeam(language=sfile.pofile.language.pk, project=sfile.pofile.release.project.pk)
            teams.add(h)
        except Exception, e:
            logger.error("Submit Queue: %s" % (e))
            
    if len(teams) == 0:
        messages.warning(request, _("You are not authorized to perform this action."))
        return HttpResponseRedirect(back)
        
    for tm in teams:
        try:
            t = Team.objects.get(language=tm.language, project=tm.project)
            if not t.can_commit(request.user):
                messages.warning(request, _("You are not authorized to perform this action."))        
                return HttpResponseRedirect(back)
        except:
            logger.error("Team %s-%s not found" % (tm.language, tm.project))
            messages.warning(request, _("You are not authorized to perform this action."))     
            return HttpResponseRedirect(back)

    if len(files)==0:
        messages.warning(request, _("Please, select one or more files."))
        return HttpResponseRedirect(back)

    if reject:
        needuser = False
        form = RejectSubmitForm()
        messages.info(request, _("You are about to reject the following files."))
    else:
        if t.project.repo_user:
            needuser=False
            form = CommentForm()
        else:
            needuser=True
            form = HttpCredForm()
        messages.info(request, _("You are about to submit the following files."))
    
    return render_to_response("files/file_submit_confirm.html",
                               {'files': files,
                                'back': back,
                                'form': form,
                                'reject': reject,
                                'needuser': needuser,
                                'project': t.project.pk},
                               context_instance = RequestContext(request))

@login_required
def confirm_submit(request):    

    if request.method != 'POST':
        raise Http403

    if request.POST.has_key('reject') and request.POST.get('reject')=='True':
        reject = True;
    else:
        reject = False
    if request.POST.has_key('needuser') and request.POST.get('needuser')=='False':
        needuser = False;
    else:
        needuser = True

    if reject:
        form = RejectSubmitForm(request.POST)
    else:
        if needuser: 
            form = HttpCredForm(request.POST)
        else:
            form = CommentForm(request.POST)
        
    if not form.is_valid():
        files = []
        for fid in request.POST.getlist('file'):
            try:
                sfile = POFileSubmit.objects.get(pk=fid)
                files.append(sfile)
            except:
                pass            
        messages.warning(request, message=_("Complete the form and try again."))
        return render_to_response("files/file_submit_confirm.html",
                                   {'files': files,
                                    'back': request.POST['back'],
                                    'form': form,
                                    'reject': reject},
                                   context_instance = RequestContext(request))

    files = []
    for fid in request.POST.getlist('file'):
        try:
            submfile = POFileSubmit.objects.get(pk=fid)
            if reject:
                send_pm(submfile.owner, _("Submit rejected"), message=_("The file %(file)s (%(project)s) was rejected by %(user)s [%(comment)s]") % 
                                        {'file': submfile.pofile.filename,
                                         'user': request.user.username,
                                         'project': submfile.pofile.release.project.name,
                                         'comment': form.cleaned_data.get('message')},)
                POFileLog.objects.create(pofile=submfile.pofile,
                                         user=request.user, action='X',
                                         comment=form.cleaned_data.get('message'))
                #file.pofile.locks.get().delete()
                #submfile.delete()
                submfile.status = SUBMIT_STATUS_ENUM.REJECTED
                submfile.save()
            else:
                files.append(submfile)
#                c = CommitQueue.objects.create(submit=file,
#                                               owner=request.user,
#                                               repo_user=form.cleaned_data.get('user'),
#                                               repo_pwd=form.cleaned_data.get('password'))
        except:
            pass

    if reject:
        messages.info(request, message=_("The files were rejected."))
                
    if len(files)>0:
        if needuser:
            puser = form.cleaned_data.get('user')
            ppass = form.cleaned_data.get('password')
        else:
            p = get_object_or_404(Project,pk=request.POST.get('p'))
            puser = p.repo_user
            ppass = p.get_repo_pwd()
            
        do_commit(request, files,
                 request.user,
                 puser,
                 ppass,
                 form.cleaned_data.get('message'))

    return HttpResponseRedirect(request.POST['back'])

def do_commit(request, submits, user, repo_user, repo_pass, message=''):
    if deferredhandler.deferred_enabled:
        deferredhandler.add_submits(submits, user, repo_user, repo_pass, message)
        msg = ungettext('The file was added to the queue for later processing.',
                            'The files were added to the queue for later processing.', len(submits))
        messages.info(request, message=msg)        
    else:
        c = SubmitClient(submits,
                         user,
                         repo_user,
                         repo_pass,
                         message)
        try:
            c.run()
            msg = ungettext('File submitted.',
                            'Files submitted.', len(submits))          
            messages.info(request, message=msg)
        except Exception, e:
            logger.error(e)
            logger.error(traceback.format_exc())
            messages.error(request, message=_("Failed. Reason: %s") % smart_unicode(e))
    
@login_required
def commit_queue(request, data = {}):
    logger.debug("Check if user has permissions")
    teams = None
    if request.user.is_superuser:
        teams = list(Team.objects.all())
    else:
        teams = list(request.user.committer.all())
        teams.extend(list(request.user.team_coordinator.all())) 

    if not teams or len(teams)==0:
        raise Http403
    
    tres = []
    for team in teams:
        po = POFileSubmit.objects.by_project_and_language(team.project, team.language)
        if po.count()>0:
            setattr(team, 'submits', po)
            tres.append(team)

    data['teams'] = tres
    
    if not data.get('form', None):
        data['form'] = UploadFileForm()
    
    return render_to_response("files/commit_queue.html",
                               data,
                               context_instance = RequestContext(request))
    
@login_required
def edit_submit_file(request, slug):
    file = get_object_or_404(POFile, slug=slug)
    redirect = HttpResponseRedirect(reverse('commit_queue'))
    if request.method == 'POST':
        if request.POST.has_key('_save'):
            form = FileEditForm(request.POST)
            if form.is_valid():
                try:
                    handle_text_file(file, form.cleaned_data['content'], request.user, form.cleaned_data['comment'])
                    messages.info(request, message=_("The file was added back to the submission queue."))
                    return redirect
                except Exception, e:
                    res = e.message.split("$$")
                    for m in res:
                        messages.error(request, message=m[:-1])
        else:
            if file.submits.all_pending():
                s = file.submits.get_pending()
                s.enabled = True
                s.save()            
            return redirect
    else:
        try:
            if file.submits.all_pending():
                s = file.submits.get_pending()
                if s.locked:
                    messages.warning(request, message=_("This file is being processed. It can't be modified."))
                    return redirect
                                                    
                s.enabled = False
                s.save()
                content = s.handler.get_content()
                messages.info(request, message=_("The file was removed from the submission queue, remember to either save your work or cancel to put the file back in the queue."))                                
            else:
                return redirect
        except:
            raise Http404
        form = FileEditForm(initial={'content': content})
    return render_to_response("files/file_edit.html",
                               {'form': form,
                                'file': file,
                                'action': reverse('edit_submit_file', kwargs={'slug': file.slug}), 
                                'title': _('Editing %s') % file.filename},
                               context_instance = RequestContext(request))
    
@login_required
def view_file_diff(request, slug, uniff=False):
    file = get_object_or_404(POFile, slug=slug)
    redirect = HttpResponseRedirect(reverse('commit_queue'))
    
    if file.submits.all_pending():
        s = file.submits.get_pending()
        content = make_file_diff(file, s, uniff)
        return render_to_response("files/file_diff.html",
                                   {'body': content,
                                    'pofile': file},
                                   context_instance = RequestContext(request))
    else:
        return redirect

def make_file_diff(file_old, file_new, uniff=False):
    content_new = file_new.handler.get_content().decode('utf-8')
    content_old = file_old.handler.get_content().decode('utf-8')
    if uniff:
        return make_udiff(content_old, content_new)
    return make_diff(content_old, content_new)
    
#def make_diff(a, b):
#    dm = diff_match_patch()
#    diffs = dm.diff_lineMode(a,b, time.time() + 60)
#    out = []
#    for (op, data) in diffs:
#      text = (data.replace("&", "&amp;").replace("<", "&lt;")
#                 .replace(">", "&gt;").replace("\n", "<br>"))
#      if op == diff_match_patch.DIFF_INSERT:
#        out.append("<ins class=\"diff_add\">%s</ins>" % text)
#      elif op == diff_match_patch.DIFF_DELETE:
#        out.append("<del class=\"diff_sub\">%s</del>" % text)
#      elif op == diff_match_patch.DIFF_EQUAL:
#        out.append("<span>%s</span>" % text)
#    return "".join(out)

def make_udiff(a, b):
    import urllib
    dm = diff_match_patch()
    diffs = dm.diff_main(a,b)
    patches = dm.patch_make(diffs)
    out = []
    for patch in patches:
        if patch.length1 == 0:
            coords1 = str(patch.start1) + ",0"
        elif patch.length1 == 1:
            coords1 = str(patch.start1 + 1)
        else:
            coords1 = str(patch.start1 + 1) + "," + str(patch.length1)
        if patch.length2 == 0:
            coords2 = str(patch.start2) + ",0"
        elif patch.length2 == 1:
            coords2 = str(patch.start2 + 1)
        else:
            coords2 = str(patch.start2 + 1) + "," + str(patch.length2)
        text = ["@@ -", coords1, " +", coords2, " @@\n"]
        # Escape the body of the patch with %xx notation.
        for (op, data) in patch.diffs:
            data = data.encode("utf-8")
            txt = urllib.quote(data, "\"!~*'();/?:@&=+$,# ")
            #txt = (data.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br>"))            
            if op == diff_match_patch.DIFF_INSERT:
                text.append("<ins class=\"diff_add\">+%s</ins>" % txt)
            elif op == diff_match_patch.DIFF_DELETE:
                text.append("<del class=\"diff_sub\">-%s</del>" % txt)
            elif op == diff_match_patch.DIFF_EQUAL:
                text.append("<span>%s</span>" % txt)
            # High ascii will raise UnicodeDecodeError.  Use Unicode instead.
        out.append("".join(text))
    return "".join(out)

def make_diff(a, b):
    dm = diff_match_patch()
    diffs = dm.diff_main(a,b)
    dm.diff_cleanupSemantic(diffs)
    out = []
    for (op, data) in diffs:
        text = (data.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br>"))
        if op == diff_match_patch.DIFF_INSERT:
            out.append("<ins class=\"diff_add\">%s</ins>" % text)
        elif op == diff_match_patch.DIFF_DELETE:
            out.append("<del class=\"diff_sub\">%s</del>" % text)
        elif op == diff_match_patch.DIFF_EQUAL:
            out.append("<span>%s</span>" % text)
    return "".join(out)
    
def make_diff_old(a, b):
    import difflib
    filename = hash(b.encode('utf-8')).hexdigest()
    fc = FileCache(filename, expireInMinutes = None, tempdir = settings.TEMP_UPLOAD_PATH, prefix = '')
    try:
        content = fc.load()
    except:
        logger.exception('load')
        content = None
    if not content:
        out = []
        s = difflib.SequenceMatcher(None, a, b)
        for e in s.get_opcodes():
            if e[0] == "replace":
                out.append('<del class="diff_chg">'+''.join(a[e[1]:e[2]]) + '</del><ins class="diff_add">'+''.join(b[e[3]:e[4]])+"</ins>")
            elif e[0] == "delete":
                out.append('<del class="diff_sub">'+ ''.join(a[e[1]:e[2]]) + "</del>")
            elif e[0] == "insert":
                out.append('<ins class="diff_add">'+''.join(b[e[3]:e[4]]) + "</ins>")
            elif e[0] == "equal":
                out.append(''.join(b[e[3]:e[4]]))
            else: 
                raise "Um, something's broken. I didn't expect a '" + `e[0]` + "'."
        content = ''.join(out)
        try:
            fc.save(content)
        except:
            logger.exception('save')
    return content

@login_required
def do_merge(request, slug):
    pofile = get_object_or_404(POFile, slug=slug)
    
    redirect = HttpResponseRedirect(reverse('list_files',
                            kwargs={'release': pofile.release.slug,
                              'language': pofile.language.code}))

    team = Team.objects.get(project=pofile.component.project, language=pofile.language)
    if not team.is_member(request.user) and not team.can_manage(request.user):
        messages.warning(request, message=_("You are not a member of this team."))                
        return redirect            
    
    if pofile.submits.all_pending():
        messages.warning(request, message=_("The file has a pending submit. You can't force a merge right now."))
        return redirect

    if not pofile.potfile.all():
        messages.error(request, message=_('POT file not found.'))
        return redirect
    
    try:
        filehandler.process_merge(pofile, request.user)
    except Exception, e:
        messages.error(request, message=str(e))
    else:
        messages.info(request, message=_("File merged and added to the submission queue."))

    return redirect
    
@render("files/file_detail.html")
def file_detail(request, slug):
    pofile = get_object_or_404(POFile, slug=slug)
    return {'pofile': pofile}

def create_diff_cache(submits):
    for s in submits:
        logger.debug("Processing diff for %s" % s.pofile.filename)
        make_file_diff(s.pofile, s)

@login_required
def submit_new_file(request, slug):

    if request.method != 'POST':
        raise Http403
    
    pofile = get_object_or_404(POFile, slug=slug)
    
    back = reverse('commit_queue')

    team = get_object_or_404(Team, language=pofile.language.pk, project=pofile.release.project.pk)
    if not team.can_commit(request.user):
        messages.warning(request, message=_("You are not authorized to perform this action."))        
        return HttpResponseRedirect(back)

    if pofile.submits.all_pending():
        s = pofile.submits.get_pending()
        if s.locked:
            messages.warning(request, message=_("This file is being processed. It can't be modified."))
            return back
        s.enabled = False
        s.save()    

    res = {}
    res['back']=back
    res['uploadfile']=pofile
    
    form = UploadFileForm(request.POST, request.FILES)
    
    if form.is_valid():
        try:
            logger.debug(request.FILES)
            # first we add the files to the queue
            submits = handle_uploaded_file(request.FILES['file'], pofile.release, pofile.language, request.user, form.cleaned_data['comment'], pofile)
            messages.info(request, message=_("Your file was uploaded and added to the submission queue."))
            return HttpResponseRedirect(back)
        except Exception, e:
            s.enabled = True
            s.save()    
            logger.error(e)
            res['message']=e.message.split("$$")
            return render_to_response('files/upload_failed.html',
                                      res,
                                      context_instance = RequestContext(request))
    else:
        s.enabled = True
        s.save()
        res['form']=form

    return commit_queue(request, res)