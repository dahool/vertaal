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
from django.utils.translation import ugettext as _
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.template.context import RequestContext
from djangoutils.render.shortcuts import XMLResponse
from django.template.loader import render_to_string
from django.conf import settings
from django.views.decorators.cache import cache_page
from django.contrib.auth.models import User

from djangopm.models import PMMessage, PMInbox, PMOutbox
from djangopm.forms import MessageForm

from common.middleware.exceptions import Http403

import datetime
from files.views import ResponseMessage


MAX_DISPLAY = getattr(settings, 'PM_COUNT_DISPLAY', 50)

@login_required
def home(request):
    messages = request.user.pm_inbox.all()[:MAX_DISPLAY]
    return render_to_response("djangopm/mailbox.html", {'pmmessages': messages}, context_instance = RequestContext(request))

@login_required
def inbox(request):
    messages = request.user.pm_inbox.all()[:MAX_DISPLAY]
    return render_to_response('djangopm/message_list.html',
                            {'pmmessages': messages, 'isinbox': True}, 
                            context_instance = RequestContext(request))

@login_required
def outbox(request):
    messages = request.user.pm_outbox.all()[:MAX_DISPLAY]
    return render_to_response('djangopm/message_list.html',
                            {'pmmessages': messages}, 
                            context_instance = RequestContext(request))

@login_required
def draftbox(request):
    messages = request.user.pmmessage_set.filter(draft=True)[:MAX_DISPLAY]
    return render_to_response('djangopm/message_list.html',
                            {'pmmessages': messages, 'compose': 'compose'}, 
                            context_instance = RequestContext(request))

@login_required
@cache_page(60 * 30) 
def inbox_detail(request, id):
    message = get_object_or_404(request.user.pm_inbox, pk=id)
    if message.unread:
        message.unread = False
        message.notified = datetime.datetime.now();
        message.save() 
    return render_to_response('djangopm/message_detail.html',
                            {'pmmessage': message.message}, 
                            context_instance = RequestContext(request))
    
@login_required
@cache_page(60 * 30)
def outbox_detail(request, id):
    message = get_object_or_404(request.user.pm_outbox, pk=id)
    return render_to_response('djangopm/message_detail.html',
                            {'pmmessage': message.message}, 
                            context_instance = RequestContext(request))  

@login_required
def inbox_delete(request):
    if request.method != 'POST':
        raise Http403
    request.user.pm_inbox.filter(id__in=request.POST.getlist('id')).delete()
    return XMLResponse({'pk': request.POST.getlist('id')})
    
@login_required    
def message_detail(request, id):
    message = get_object_or_404(PMMessage, pk=id)
    form = MessageForm(instance=message)
    return render_to_response('djangopm/message_compose.html',
                            {'form': form, 'recipients': message.recipients.all(), 'instance': message}, 
                            context_instance = RequestContext(request))          
    
@login_required    
def message_submit(request):
    if request.method == "POST":
        res = {}
        instance = None
        action = request.POST.get('action')
        current = request.POST.get('id', None)
        if current:
            instance = get_object_or_404(PMMessage, pk=current)
        form = MessageForm(request.POST, instance=instance)
        if form.is_valid():
            if action == 'send' and len(form.cleaned_data['recipients']) > 0:
                form.save(request.user, send=True)
                return XMLResponse({'message': ResponseMessage.success(_('Message sent.'))})
            elif action != 'send':
                form.save(request.user, send=False)
                return XMLResponse({'message': ResponseMessage.success(_('Message saved as draft.'))})
            else:
                res['message'] = ResponseMessage.error(_("You didn't select any recipient")); 
        
        recipients = []
        for ri in request.POST.getlist('recipients'):
            try:
                u = User.objects.get(pk=ri)
                recipients.append(u)
            except:
                pass

        res['content_HTML'] = render_to_string('djangopm/message_compose.html',
                                  {'form': form, 'recipients': recipients, 'instance': instance}, 
                                      context_instance = RequestContext(request))
        return XMLResponse(res)
    else:
        raise Http403