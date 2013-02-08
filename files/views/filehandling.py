# -*- coding: utf-8 -*-
"""Copyright (c) 2013, Sergio Gabriel Teves
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
import re
import logging
import pygments
import pygments.lexers
import pygments.formatters
    
from django.utils.translation import ugettext as _
from django.shortcuts import render_to_response, get_object_or_404
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.core.cache import cache
from django.shortcuts import redirect
from django.contrib import messages

import files.lib.handlers as filehandler
from teams.models import Team
from files.models import POFile, POFileSubmit, POFileLock
from files.forms import FileEditForm
from files.views import check_status
    
logger = logging.getLogger(__name__)

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
                    filehandler.handle_text_file(file, form.cleaned_data['content'], request.user, form.cleaned_data['comment'])
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
    
@login_required
def edit_submit_file(request, slug):
    file = get_object_or_404(POFile, slug=slug)
    redirect = HttpResponseRedirect(reverse('commit_queue'))
    if request.method == 'POST':
        if request.POST.has_key('_save'):
            form = FileEditForm(request.POST)
            if form.is_valid():
                try:
                    filehandler.handle_text_file(file, form.cleaned_data['content'], request.user, form.cleaned_data['comment'])
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