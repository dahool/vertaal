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
import logging

from django.utils.translation import ugettext as _
from django.utils.encoding import smart_unicode
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext 
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from django.contrib.auth.models import User
from django.db.models import Q
from django.contrib import messages
from djangopm.utils import send_pm
from django.conf import settings

from common.middleware.exceptions import Http403
from common.simplexml import XMLResponse
from common.i18n import set_user_language
from common.view.decorators import render

from files.models import LOG_ACTION, POFile, POFileLog, POFileAssign
from teams.models import Team
from releases.models import Release
from languages.models import Language
from components.models import Component

from files.views import check_status

logger = logging.getLogger(__name__)

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

def file_log(request, slug):
    file = get_object_or_404(POFile,slug=slug)
    return render_to_response("files/file_log.html",
                              {'pofile': file},
                              context_instance = RequestContext(request))
    
@render("files/file_detail.html")
def file_detail(request, slug):
    pofile = get_object_or_404(POFile, slug=slug)
    return {'pofile': pofile}



