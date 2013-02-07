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
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.template.context import RequestContext
from djangoutils.render.shortcuts import XMLResponse
from django.template.loader import render_to_string
from djangopm.models import PMMessage, PMInbox, PMOutbox
from django.conf import settings
from djangopm.forms import MessageForm

import datetime
from common.middleware.exceptions import Http403

MAX_DISPLAY = getattr(settings, 'PM_COUNT_DISPLAY', 50)

@login_required
def home(request):
    form = MessageForm()
    return render_to_response("djangopm/mailbox.html", {'form': form}, context_instance = RequestContext(request))

@login_required
def inbox(request):
    messages = request.user.pm_inbox.all()[:MAX_DISPLAY]
    return render_to_response('djangopm/message_list.html',
                            {'messages': messages}, 
                            context_instance = RequestContext(request))

@login_required
def outbox(request):
    messages = request.user.pm_outbox.all()[:MAX_DISPLAY]
    return render_to_response('djangopm/message_list.html',
                            {'messages': messages}, 
                            context_instance = RequestContext(request))

@login_required
def draftbox(request):
    messages = request.user.pmmessage_set.filter(draft=True)[:MAX_DISPLAY]
    return render_to_response('djangopm/message_list.html',
                            {'messages': messages}, 
                            context_instance = RequestContext(request))

@login_required    
def inbox_detail(request, id):
    message = get_object_or_404(request.user.pm_inbox, pk=id)
    #message = get_object_or_404(PMInbox, pk=id)
    if message.unread:
        message.unread = False
        message.notified = datetime.datetime.now();
        message.save() 
    return XMLResponse({'pk': id})
#    return render_to_response('djangopm/message_detail.html',
#                            {'message': message.message}, 
#                            context_instance = RequestContext(request))
    
@login_required    
def outbox_detail(request, id):
    message = request.user.pm_outbox.filter(pk=id)
    #message = get_object_or_404(PMOutbox, pk=id)
    return render_to_response('djangopm/message_detail.html',
                            {'message': message.message}, 
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
    return render_to_response('djangopm/message_detail.html',
                            {'message': message}, 
                            context_instance = RequestContext(request))          