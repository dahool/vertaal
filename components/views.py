import os
import chunk

from django.contrib.auth.decorators import login_required, permission_required
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from common.decorators import permission_required_with_403
from common.middleware.exceptions import Http403
from projects.models import Project
from releases.models import Release
from files.models import *
from components.forms import ComponentForm
from components.models import Component
from django.contrib.auth.models import User
from projects.util import get_build_log_file
from common.simplexml import XMLResponse

from django.contrib import messages

@login_required
def component_create_update(request, project=None, slug=None):
    res = {}
    if not project and not slug:
        raise Http404

    if request.method == 'POST':
        if slug:
            r = get_object_or_404(Component, slug=slug)
            res['component']=r
            res['project']=r.project
            form = ComponentForm(request.POST, instance=r)
        else:
            p = get_object_or_404(Project, slug=project)
            res['project']= p
            # just in case someone change the hidden value
            if not int(request.POST.get('project')) == int(p.id):
                raise Http403
            form = ComponentForm(request.POST)
        if form.is_valid():
            r = form.save()
            return HttpResponseRedirect(r.project.get_absolute_url())
        res['form'] = form
    else:
        if slug:
            r = get_object_or_404(Component, slug=slug)
            # CHECK IF THE USER CAN EDIT THIS
            if not r.project.is_maintainer(request.user):
                raise Http403
            res['component']=r
            res['project']=r.project
            form = ComponentForm(instance=r)
        else:
            p = get_object_or_404(Project, slug=project)
            if not p.is_maintainer(request.user):
                raise Http403
            res['project']= p
            form = ComponentForm()
        res['form'] = form 
    return render_to_response("components/component_form.html",
                              res,
                              context_instance = RequestContext(request))    

@login_required
def component_delete(request, slug=None):
    r = get_object_or_404(Component, slug=slug)
    if not r.project.is_maintainer(request.user):
        raise Http403
    p = r.project
    r.delete()
    return HttpResponseRedirect(p.get_absolute_url())

def component_detail(request, slug):
    component = get_object_or_404(Component, slug=slug)

    if not component.project.enabled:
        if component.project.is_maintainer(request.user):
                messages.warning(request, _('This project is disabled. Only maintainers can view it.'))
        else:
            raise Http403
    
    stats = POFile.objects.component_by_release_total(component)
        
    return render_to_response("components/component_detail.html",
        {'component': component,
         'stats': stats}, 
          context_instance = RequestContext(request))
