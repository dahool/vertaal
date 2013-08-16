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
from django.conf import settings
from django.utils.translation import ugettext as _
from django.template import RequestContext, loader, Context
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string
from common.middleware.exceptions import Http403
from common.simplexml import XMLResponse
from userprofileapp.models import *
from userprofileapp.forms import UserProfileForm

import logging
logger = logging.getLogger('vertaal.userprofile')

from django.core.mail import EmailMessage
from common.mail import send_mass_mail_em
from teams.views import ContactForm
from app.templatetags.extendtags import get_full_url

from django.contrib import messages

from teams.models import Team

from django.contrib.auth import logout as auth_logout

@login_required
def update_favorites(request, remove=False, idtype=False):
    if request.method != 'POST':
        raise Http403

    res = {}
    if remove:
        id = False
        try:
            if idtype:
                id = request.POST.get('id')
                f = Favorite.objects.get(id=id)
            else:
                path = request.POST.get('path')
                f = Favorite.objects.get(url=path)
                id = f.id
                title = ''
            f.delete()
        except Exception, e:
            logger.error(e)
        if id:
            res['id'] = id
    else:
        title = request.POST.get('title')
        path = request.POST.get('path')
        if title.count("|") > 0:
            title = title.split("|")[1]
        title = title.strip()
        try:
            f = request.user.user_favorites.create(url=path,
                                               name=title)
            id = f.id
            res['id'] = id
            res['title'] = title
            res['path'] = path            
        except Exception, e:
            logger.error(e)
            
    if not idtype:
        page = render_to_string('favs.html',
                                {'path': path},
                                context_instance = RequestContext(request))
        res['content_HTML'] = page
    return XMLResponse(res)

@login_required
def account_profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            u = form.save()
            lang = u.get_profile().language
            if lang and request.LANGUAGE_CODE <> lang:
                from django.utils import translation
                translation.activate(lang)
            messages.success(request, _("Profile updated."))            
    else:
        form = UserProfileForm(instance=request.user)
    if request.user.is_superuser:
        cform = ContactForm()
    else:
        cform = None
    return render_to_response("registration/profile.html",
                              {'form': form, 'cform': cform},
                               context_instance = RequestContext(request))

@login_required
def set_startup(request, remove=False):
    if request.method != 'POST':
        raise Http403

    res = {}
    res['id'] = fav_id = request.POST.get('id')
    profile = request.user.get_profile()
    if remove:
        res['success'] = True
        if profile.startup:
            try:
                profile.startup = None
                profile.save()
            except:
                res['success'] = False
    else:
        try:
            fav = Favorite.objects.get(id=fav_id)
            profile.startup = fav
            profile.save()
            res['success'] = True
        except:
            res['success'] = False
    return XMLResponse(res)
        
@login_required
def startup_redirect(request):
    try:
        profile = request.user.get_profile()
    except:
        profile = UserProfile.objects.create(user=request.user)
        
    if profile.startup is None:
        return HttpResponseRedirect(getattr(settings, 'STARTUP_REDIRECT_URL', reverse('user_profile')))
    else:
        return HttpResponseRedirect(profile.startup.url)

@login_required
def drop_account(request):
    if request.method == 'POST':
        pass1 = request.POST['password1']
        pass2 = request.POST['password2']
        if pass1 == pass2:
            if request.user.check_password(pass1):
                current_user = request.user
                auth_logout(request)
                UserAuditLog.objects.create(action='DELETE',username=current_user.username,ip=request.META.get('REMOTE_ADDR'))
                current_user.delete()
                #messages.success(request, _('Your account has been removed.'))
                return HttpResponseRedirect(reverse('home'))
        messages.error(request, _('The information provided is invalid.'))
        return HttpResponseRedirect(reverse('user_profile'))  
    else:
        return render_to_response("registration/drop_account.html",
                                  context_instance = RequestContext(request))
        
@login_required
def mass_notification(request):
    if request.method != 'POST' or not request.user.is_superuser:
        raise Http403
    
    form = ContactForm(request.POST)

    if form.is_valid():
        subject = form.cleaned_data['subject']
        message = form.cleaned_data['message']
        message += '\n\n--\nThe %(app_name)s administration.\n%(home)s' % {'app_name': getattr(settings, 'PROJECT_NAME'), 'home': get_full_url(reverse('home'))}

        maillist = []
        addressset = set()
        for team in Team.objects.filter(project__enabled=True):
            for u in team.team_members:
                if not u.is_superuser and not u.is_staff:
                    addressset.add(u.email)
        addresslist = list(addressset)
        for i in range(0,len(addresslist),25):
            maillist.append(EmailMessage(subject=subject, body=message, bcc=addresslist[i:i+25]))

        try:
            send_mass_mail_em(maillist)
        except Exception, e:
            logger.error(e)
            messages.warning(request, _("Your message couldn't be delivered to one or more recipients."))
        else:                              
            messages.success(request, _('Your message has been sent.'))

    return HttpResponseRedirect(reverse('user_profile'))
    
