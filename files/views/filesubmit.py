# -*- coding: utf-8 -*-
"""Copyright (c) 2012, Sergio Gabriel Teves
All rights reserved.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
from django.utils.translation import ungettext, ugettext as _
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.contrib import messages

from common.middleware.exceptions import Http403

from djangoutils.render.shortcuts import JSONResponse
from djangopm.utils import send_pm
import files.lib.handlers as filehandler
from releases.models import Release
from languages.models import Language
from teams.models import Team, HasheableTeam
from files.models import SUBMIT_STATUS_ENUM, POFile,  POFileSubmit, POFileLog, POFileSubmitSet
from files.forms import UploadFileForm

from files.views import check_status
from files.views.utils.commit import do_commit
from files.views.utils.list import get_file_list

from files.forms import RejectSubmitForm, CommentForm
from versioncontrol.forms import HttpCredForm
from projects.models import Project

import logging
logger = logging.getLogger('vertaal.files')

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
                submits = filehandler.handle_uploaded_file(request.FILES['file'], r, l, request.user, form.cleaned_data['comment'])
                # then we check if it is possible to commit now
                team = Team.objects.get(project=r.project,language=l)
                if r.project.auto_commit_enabled and team.submittype == 1 and team.can_commit(request.user):
                    if do_commit(request, submits, request.user, r.project.repo_user, r.project.get_repo_pwd()):
                        return JSONResponse({'success': True})
                    return JSONResponse({'success': False})
                else:
                    messages.success(request, _("Your file was uploaded and added to the submission queue."))
                    return JSONResponse({'success': True})
            except Exception, e:
                logger.error(e)
                msg = _('<b>Please, fix the following errors and upload the file again:</b><br/>%s') % "<br/>".join(str(e).split("$$"))
                messages.warning(request, msg)
                return JSONResponse({'success': False})
#                res['message']=e.message.split("$$")
#                return render_to_response('files/upload_failed.html',
#                                          res,
#                                          context_instance = RequestContext(request))
        #res.update(get_file_list(request, None, release, language))
        messages.error(request, _('Complete the required information and try again.'))
        return JSONResponse({'success': False})
    else:
        raise Http403
    return render_to_response('files/file_list.html',
                              res,
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
    
    files = POFileSubmit.objects.filter(pk__in=request.POST.getlist('file'))
    
    for sfile in files:
        h = HasheableTeam(language=sfile.pofile.language.pk, project=sfile.pofile.release.project.pk)
        teams.add(h)
                
#     for fid in request.POST.getlist('file'):
#         try:
#             sfile = POFileSubmit.objects.get(pk=fid)
#             files.append(sfile)
#             h = HasheableTeam(language=sfile.pofile.language.pk, project=sfile.pofile.release.project.pk)
#             teams.add(h)
#         except Exception, e:
#             logger.error("Submit Queue: %s" % (e))
            
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

    count = len(files)
    if reject:
        needuser = False
        form = RejectSubmitForm()
        #messages.info(request, _("You are about to reject the following files."))
        msg = ungettext('You are about to reject 1 file', 'You are about to reject %(count)s files', count) % {
            'count': count,
        }        
    else:
        if t.project.repo_user:
            needuser=False
            form = CommentForm()
        else:
            needuser=True
            form = HttpCredForm()
        #messages.info(request, _("You are about to submit the following files."))
        msg = ungettext('You are about to submit 1 file', 'You are about to submit %(count)s files', count) % {
            'count': count,
        }        
    messages.info(request, msg)
    
    fileSet = POFileSubmitSet.objects.create()
    #fileSet.files.add(*files.all())
    fileSet.files = files
    
    return render_to_response("files/file_submit_confirm.html",
                               {'files': fileSet,
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
#         files = []
#         for fid in request.POST.getlist('file'):
#             try:
#                 sfile = POFileSubmit.objects.get(pk=fid)
#                 files.append(sfile)
#             except:
#                 pass            
        messages.warning(request, message=_("Complete the form and try again."))
        return render_to_response("files/file_submit_confirm.html",
                                   {'files': request.POST.get('file'),
                                    'back': request.POST['back'],
                                    'form': form,
                                    'reject': reject},
                                   context_instance = RequestContext(request))

    files = []
    fileSet = get_object_or_404(POFileSubmitSet, pk=request.POST.get('file'))
    for submfile in fileSet.files.all():
        if reject:
            send_pm(submfile.owner, _("Submit rejected"), message=_("The file %(file)s (%(project)s) was rejected by %(user)s [%(comment)s]") % 
                                    {'file': submfile.pofile.filename,
                                     'user': request.user.username,
                                     'project': submfile.pofile.release.project.name,
                                     'comment': form.cleaned_data.get('message')},)
            POFileLog.objects.create(pofile=submfile.pofile,
                                     user=request.user, action='X',
                                     comment=form.cleaned_data.get('message'))
            submfile.status = SUBMIT_STATUS_ENUM.REJECTED
            submfile.save()
        else:
            files.append(submfile)
    
#     for fid in request.POST.getlist('file'):
#         try:
#             submfile = POFileSubmit.objects.get(pk=fid)
#             if reject:
#                 send_pm(submfile.owner, _("Submit rejected"), message=_("The file %(file)s (%(project)s) was rejected by %(user)s [%(comment)s]") % 
#                                         {'file': submfile.pofile.filename,
#                                          'user': request.user.username,
#                                          'project': submfile.pofile.release.project.name,
#                                          'comment': form.cleaned_data.get('message')},)
#                 POFileLog.objects.create(pofile=submfile.pofile,
#                                          user=request.user, action='X',
#                                          comment=form.cleaned_data.get('message'))
#                 submfile.status = SUBMIT_STATUS_ENUM.REJECTED
#                 submfile.save()
#             else:
#                 files.append(submfile)
#         except:
#             pass

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

    fileSet.delete()
    
    return HttpResponseRedirect(request.POST['back'])
    
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
            submits = filehandler.handle_uploaded_file(request.FILES['file'], pofile.release, pofile.language, request.user, form.cleaned_data['comment'], pofile)
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

@login_required
def confirm_submit_files(request, id):
    fileSet = get_object_or_404(POFileSubmitSet, pk=id)

    return render_to_response("files/file_submit_confirm_filelist.html",
                               {'fileSet': fileSet},
                               context_instance = RequestContext(request))
