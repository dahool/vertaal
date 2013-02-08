import threading
import os

from django.utils.translation import ugettext as _
from django.contrib.auth.decorators import login_required, permission_required
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.views.generic.list_detail import object_detail, object_list
from common.decorators import permission_required_with_403
from common.middleware.exceptions import Http403
from projects.forms import ProjectForm
from components.models import Component
from releases.models import Release
from languages.models import Language
from models import Project
from versioncontrol.manager import Manager, POTUpdater
from versioncontrol.models import BuildCache
from common.utils import lock
from django.contrib.auth.models import User
from projects.util import get_build_log_file, check_project
from app.log import (logger)
from files.models import POTFile, POFile

from django.contrib import messages
from djangopm.utils import send_pm

@login_required
def project_create_update(request, slug=None):
    res = {}
    if request.method == 'POST':
        if slug:
            p = get_object_or_404(Project, slug=slug)
            res['project']=p
            form = ProjectForm(request.POST, instance=p)
        else:
            form = ProjectForm(request.POST)
        if form.is_valid():
            if not unicode(request.user.id) in form.cleaned_data["maintainers"]:
                form.cleaned_data["maintainers"].append(unicode(request.user.id))
            p = form.save(True)
            if slug:
                messages.success(request, _('Updated project %s') % p.name)
            else:
                messages.success(request, _('Created project %s') % p.name)            
            return HttpResponseRedirect(p.get_absolute_url())
        messages.warning(request, _('Please, correct the following errors and try again.'))
        res['form'] = form
    else:
        if slug:
            p = get_object_or_404(Project, slug=slug)
            # CHECK IF THE USER CAN EDIT THIS PROJECT
            if not p.is_maintainer(request.user):
                raise Http403
            res['project']=p
            form = ProjectForm(instance=p)
        else:
            if not request.user.has_perm('projects.can_add'):
                raise Http403
            form = ProjectForm(initial={'maintainers': [ request.user.pk ]})
        res['form'] = form 
    return render_to_response("projects/project_form.html",
                              res,
                              context_instance = RequestContext(request))    

@permission_required_with_403('projects.can_delete')
def project_delete(request, slug=None):
    '''
    projects can be deleted by staff members only
    '''
    p = get_object_or_404(Project, slug=slug)
    p.delete()
    messages.success(request, _('Removed project %s') % p.name)
    return HttpResponseRedirect(reverse('project_list'))

@login_required
def project_build(request, release_slug):
    release = get_object_or_404(Release, slug=release_slug)

    if not release.project.is_maintainer(request.user):
        raise Http403
    
    back = HttpResponseRedirect(reverse('release_detail',kwargs={'slug': release_slug}))

    try:
        b = BuildCache.objects.get_locked(release)
        if b.count()>0:
            messages.warning(request, message=_('Build is already running.'))
            return back
    except:
        pass
    #__build_repo(release.project, release, component, request.user, b)
    t = threading.Thread(target=__build_repo,
                         name="build_%s" % release.slug,
                         kwargs={'project': release.project,
                                 'release': release,
                                 'user': request.user})
    t.start()

    messages.info(request, message=_('Build started.'))
            
    return back

def __build_repo(project, release, user):
    
    logfile = get_build_log_file(project.slug, release.slug)

    if os.path.exists(logfile):
        try:
            os.unlink(logfile)
        except Exception, u:
            logger.error("Unable to remove current logfile [%s]." % logfile)
    
#    # create a lock for console 
#    lockfile = logfile + ".lock"
#    open(lockfile).close()
#    
    # the components will remain locked for all the process
    locks = []
    try:
        for component in project.components.all():
            canbuild = True
            rev = None
            try:
                b = BuildCache.objects.get(component=component,
                                           release=release)
                if b.is_locked:
                    canbuild = False
                    send_pm(user, subject=_('Component %s is locked at this moment.') % component.name)  
                    logger.debug('Component %s is locked.' % component.name)                  
                else:
                    b.lock()
            except BuildCache.DoesNotExist:
                b = BuildCache.objects.create(component=component,
                                           release=release)
                b.lock()
            except Exception, e:
                send_pm(user, _("Build error"), str(e))
                logger.error(e)
                raise
            if canbuild:
                locks.append(b)
                for team in project.teams.all():
                    
                    if (POFile.objects.filter(release=release,
                                          component=component,
                                          language=team.language).count()) == 0:
                        logger.debug("New language %s" % team.language)
                        new_team = True
                    else:
                        logger.debug("Rebuild language %s" % team.language)
                        new_team = False
                    
                    repo = Manager(project, release, component, team.language, logfile)
                    try:
                        b.setrev(repo.build())
#                        send_pm(user, subject=_('Build of %(component)s on release %(release)s for team %(team)s completed.')
#                                        % {'component': component.name,
#                                           'release': release.name,
#                                           'team': team.language.name})
                    except lock.LockException, l:
                        repo.notify_callback(l)
                        logger.error(l)
                        send_pm(user, _("Project locked"), message=_('Project locked for %(team)s. Try again in a few minutes. If the problem persist contact the administrator.') % {
                                            'team': team.language.name})
                    except Exception, e:
                        repo.notify_callback(e)
                        logger.error(e)
                        send_pm(user, _('Error building team %(team)s.') % {'team': team.language.name}, _('Reason: %(error)s') % {'error': e.args} )
                    finally:
                        del repo
                
                send_pm(user, _('Finished build cache for component %(component)s.') %
                                {'component': component.name})
                
                if component.potlocation:
                    repo = POTUpdater(project, release, component, logfile)
                    try:
                        repo.build()
                        
                        if new_team:
                            potfiles = POTFile.objects.filter(release=release,
                                                              component=component)
                            for potfile in potfiles:
                                repo.add_pofiles(potfile)
                            
                    except lock.LockException, l:
                        repo.notify_callback(l)
                        logger.error(l)
                        send_pm(user, _("Project locked"), message=_('Project %s locked. Try again in a few minutes. If the problem persist contact the administrator.') % project.name)
                    except Exception, e:
                        repo.notify_callback(e)
                        logger.error(e)
                        send_pm(user, _("Build error"), message=_('Build error. Reason: %(error)s') % {
                                            'error': e.args})
                    finally:
                        del repo
                        
    except Exception, e:
        logger.error(e)
    finally:
        # unlock all components
        for l in locks:
            l.unlock()
        try:
            del repo
        except:
            pass
        message=_('Finished build cache for release %(release)s.') % {'release': release.name}
        send_pm(user, "Build complete", message=message)
        user.email_user(_('Build complete'), message)

def project_list(request):
    list = Project.objects.by_authorized(request.user)
    return object_list(request,
                         queryset=list,
                         template_object_name= 'project')    
    
def project_detail(request, slug):
    p = get_object_or_404(Project, slug=slug)

    if not p.enabled:
        if p.is_maintainer(request.user):
            messages.info(request, message=_('This project is disabled. Only maintainers can view it.'))
        else:
            raise Http403
    
    if p.is_maintainer(request.user):
        return object_detail(request,
                             queryset=Project.objects.all(),
                             template_object_name= 'project',
                             slug=slug,
                             extra_context={
                                    'languages': Language.objects.get_unused(p)
                                    })
    else:
        return object_detail(request,
                             queryset=Project.objects.all(),
                             template_object_name= 'project',
                             slug=slug)
