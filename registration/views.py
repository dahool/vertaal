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
from django.utils.translation import ugettext as _
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from common.middleware.exceptions import Http403

from registration.forms import *
from django.conf import settings
from djangoutils.render.shortcuts import XMLResponse, JSONResponse

if settings.USE_CAPTCHA:
    from recaptcha.client import captcha

def register(request):
    captcha_error = ""
    captcha_valid = True
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if settings.USE_CAPTCHA:        
            captcha_response = captcha.submit(request.POST.get("recaptcha_challenge_field", None),  
                                           request.POST.get("recaptcha_response_field", None),  
                                           settings.RECAPTCHA_PRIVATE_KEY,  
                                           request.META.get("REMOTE_ADDR", None))  
            captcha_valid = captcha_response.is_valid
        if not captcha_valid:  
            captcha_error = "&error=%s" % captcha_response.error_code 
        else:
            if form.is_valid():
                u = form.save()
                msg = render_to_string('registration/welcome.mail',
                            {'username': u.username},
                            context_instance = RequestContext(request))    
                u.email_user(_('Welcome to %(project)s') % {'project':settings.PROJECT_NAME}, msg)
                return render_to_response("contact/message.html",
                                          {'message': _('You can now sign in with the choosen username and password.')},
                                          context_instance = RequestContext(request))
    else:
        if request.user.is_authenticated():
            return HttpResponseRedirect(reverse('home'))
        
        form = RegistrationForm()
    return render_to_response("registration/register.html",
                              {'form': form,
                               'captcha_error': captcha_error,
                               'settings': settings},
                               context_instance = RequestContext(request))
@login_required
def query_user(request):
    if request.method != 'POST':
        raise Http403
    
    text = request.POST.get('search')
    users = User.objects.filter(username__icontains=text)
    
    if 'application/json' in request.META.get('HTTP_ACCEPT',[]):
        data = []
        for user in users:
            data.append({'pk': user.pk, 'username': user.username})
        return JSONResponse({'result': data})
    else:
        page = render_to_string('registration/user_query_response.html',
                                {'users': users},
                                context_instance = RequestContext(request))    
        res={}
        res['content_HTML'] = page
        return XMLResponse(res)