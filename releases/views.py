# -*- coding: utf-8 -*-
"""Copyright (c) 2012 Sergio Gabriel Teves
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
import os

from django.utils.translation import ugettext as _
from django.utils.encoding import smart_unicode
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404

from common.middleware.exceptions import Http403
from projects.models import Project
from projects.util import get_build_log_file
from releases.forms import ReleaseForm
from releases.models import Release
from files.models import POFile, POFileAssign
from teams.models import Team
from common.simplexml import XMLResponse
from versioncontrol.models import BuildCache

from versioncontrol.forms import HttpCredForm
from files.forms import CommentForm

from django.contrib import messages

import logging
logger = logging.getLogger('vertaal.releases')

@login_required
def release_create_update(request, project=None, slug=None):
    res = {}
    if not project and not slug:
        raise Http404

    if request.method == 'POST':
        if slug:
            r = get_object_or_404(Release, slug=slug)
            res['release']=r
            res['project']=r.project
            form = ReleaseForm(request.POST, instance=r)
        else:
            p = get_object_or_404(Project, slug=project)
            res['project']= p
            # just in case someone change the hidden value
            if not int(request.POST.get('project')) == int(p.id):
                raise Http403
            form = ReleaseForm(request.POST)
        if form.is_valid():
            r = form.save()
            if slug:
                messages.success(request, _('Updated release %s') % r.name)
            else:
                messages.success(request, _('Created release %s') % r.name)
            return HttpResponseRedirect(r.project.get_absolute_url())
        messages.warning(request, _('Please, correct the following errors and try again.'))
        res['form'] = form
    else:
        if slug:
            r = get_object_or_404(Release, slug=slug)
            # CHECK IF THE USER CAN EDIT THIS
            if not r.project.is_maintainer(request.user):
                raise Http403
            res['release']=r
            res['project']=r.project
            form = ReleaseForm(instance=r)
        else:
            p = get_object_or_404(Project, slug=project)
            if not p.is_maintainer(request.user):
                raise Http403
            res['project']= p
            form = ReleaseForm()
        res['form'] = form 
    return render_to_response("releases/release_form.html",
                              res,
                              context_instance = RequestContext(request))    

@login_required
def release_delete(request, slug=None):
    r = get_object_or_404(Release, slug=slug)
    if not r.project.is_maintainer(request.user):
        raise Http403
    p = r.project
    r.delete()
    messages.success(request, _('Removed release %s') % r.name)
    return HttpResponseRedirect(p.get_absolute_url())

def release_detail(request, slug):
    r = get_object_or_404(Release, slug=slug)

    if not r.enabled or not r.project.enabled:
        if r.project.is_maintainer(request.user):
            if not r.project.enabled:
                messages.info(request, message=_('This project is disabled. Only maintainers can view it.'))
            else:
                messages.info(request, message=_('This release is disabled. Only project maintainers can view it.'))
        else:
            raise Http403
    
    stats = POFile.objects.by_release_total(r)

    logfile = get_build_log_file(r.project.slug, r.slug)
    if not os.path.exists(logfile):
        logfile = False
    
    if request.user.is_authenticated():
        is_coord = request.user.team_coordinator.filter(project=r.project).count()>0
    else:
        is_coord = False
        
    return render_to_response("releases/release_detail.html",
                              {'release': r,
                               'stats': stats,
                               'build_log': logfile,
                               'is_coord': is_coord},
                              context_instance = RequestContext(request))
    
@login_required
def release_populate(request, slug):
    release = get_object_or_404(Release, slug=slug)

    if (not release.project.is_maintainer(request.user) and
         request.user.team_coordinator.filter(project=release.project).count()==0):
        raise Http403
    
    back = HttpResponseRedirect(reverse('release_detail', kwargs={'slug':slug}))
    if request.method == 'POST':
        release_from = get_object_or_404(Release, pk=request.POST.get('copy_from'))
        for lang_id in request.POST.getlist('language_id'):
            for pofile in POFile.objects.filter(release=release_from,language__id=lang_id, assigns__isnull=False):
                try:
                    to_pofile = POFile.objects.get(release=release,
                                                      component=pofile.component,
                                                      language=pofile.language,
                                                      filename=pofile.filename,
                                                      assigns__isnull=True)
                except:
                    logger.debug("Skipped file %s" % smart_unicode(pofile))
                else:
                    assign = pofile.assigns.get()
                    asg = POFileAssign(pofile=to_pofile)
                    if assign.translate and assign.translate.is_active:
                        asg.translate = assign.translate
                    if assign.review and assign.review.is_active:
                        asg.review = assign.review
                    asg.save()
        messages.success(request, _('Success.'))
        return back
    else:
        releases = Release.objects.filter(project=release.project).exclude(pk=release.pk)
        if releases.count() == 0:
            messages.warning(request, _('There are no available releases to populate from.'))
            return back
        if release.project.is_maintainer(request.user):
            languages = [team.language for team in Team.objects.filter(project=release.project)]
        else:
            languages = [team.language for team in request.user.team_coordinator.filter(project=release.project)]
        return render_to_response('releases/release_populate.html',
                                {'release': release,
                                 'releases': releases,
                                 'languages': languages},
                                 context_instance = RequestContext(request))
    
        
    
@login_required
def build_log(request, project, release):

    logfile = get_build_log_file(project, release)
    if not os.path.exists(logfile):
        raise Http404
    
    release = Release.objects.get(slug=release)
    
    if request.method == 'POST':
        res = {}
        offset = request.POST.get('offset')
        try:
            f = file(logfile)
            f.seek(long(offset))
            res['text_HTML'] = f.read().replace('\n','<br/>')
            res['offset'] = f.tell()
        except EOFError:
            res['offset']=offset
        finally:
            f.close()
            
        try:
            b = BuildCache.objects.get_locked(release=release)
            logger.debug("Locks count: %s" % b.count())
            if b.count()==0:
                res['offset']='END'   
        except Exception, e:
            logger.error(e)
            res['offset']='END'
            
        if res['offset']=='END':
            res['text_HTML'] += '<br/><< EOF >>' 
        return XMLResponse(res)
    else:
        return render_to_response("releases/release_build_console.html",
            {'release': release}, 
              context_instance = RequestContext(request))
        
@login_required
def multimerge(request, slug):
    release = get_object_or_404(Release,slug=slug)

    is_coord = request.user.team_coordinator.filter(project=release.project).count()>0
    is_maintainer = release.project.is_maintainer(request.user)
    
    if not is_coord and not is_maintainer:
        raise Http403

    teams = None
    
    if request.method == 'POST':
        redirect = True
        files = []
        
        for fid in request.POST.getlist('file'):
            files.append(POFile.objects.get(pk=fid))
        
        if len(files)==0:
            raise Http404
        
        from files.lib.handlers import process_merge
        
        fail=[]
        submitted = []
        for pofile in files:
            try:
                submitted.append(process_merge(pofile, request.user))
            except Exception, e:
                logger.error(e)
                fail.append(pofile)
        
        if len(fail)>0:
            if len(fail) == len(files):
                messages.error(request, _("The files could not be merged."))
                redirect = False
            else:
                messages.warning(request, _("Some files could not be merged."))

        if redirect:
            if release.project.repo_user:
                needuser=False
                form = CommentForm()
            else:
                needuser=True
                form = HttpCredForm()
            messages.info(request, _("You are about to submit the following files."))
            return render_to_response("files/file_submit_confirm.html",
                               {'files': submitted,
                                'back': reverse('multimerge', kwargs={'slug': slug}),
                                'form': form,
                                'needuser': needuser,
                                'reject': False,
                                'project': release.project.pk},
                               context_instance = RequestContext(request))            
        
    if is_maintainer:
        logger.debug("User is maintainer")
        teams = list(Team.objects.filter(project=release.project))
    else:
        logger.debug("User is coordinator")
        teams = list(request.user.team_coordinator.filter(project=release.project))

    if not teams or len(teams)==0:
        raise Http403

    logger.debug("%d teams" % len(teams))
    
    langlist = []
    for team in teams:
        langlist.append(team.language)
        
    filelist = POFile.objects.unmerged(langlist, release.project, release)
    
    logger.debug("File list length: %d" % len(filelist))
    
    return render_to_response("releases/release_merge.html",
                              {'release': release,
                               'files': filelist},
                              context_instance = RequestContext(request))        