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
from django.conf.urls import patterns, url, include
from django.contrib.auth import views as auth_views
from registration.views import *
from django_authopenid.views import signin as openid_signin
from django.conf import settings

urlpatterns = patterns('',
    #url(r'^signin/$', auth_views.login, name="user_signin"),                       
    url(r'^signin/$', openid_signin, name="user_signin", kwargs={"template_name":"registration/login.html"}),
    url(r'^signout/$', auth_views.logout, {'next_page': settings.LOGOUT_REDIRECT_URL }, name="user_signout"),
    #url(r'^profile/$', account_profile, name="user_profile"),
    url(r'^signup/$', register, name="user_signup"),
    url(r'^query/$', query_user, name="user_query"),
    url(r'^password_reset/$', auth_views.password_reset, name="password_reset"),
    url(r'^password_reset/done/$', auth_views.password_reset_done),
    url(r'^reset/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$', auth_views.password_reset_confirm),
    url(r'^reset/done/$', auth_views.password_reset_complete),
    #url(r'^$', account_profile),
)  
