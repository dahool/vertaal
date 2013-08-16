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
from django.conf.urls.defaults import patterns, url, include
from userprofileapp.views import *

urlpatterns = patterns('',
    url(r'^$', account_profile, name="user_profile"),
    url(r'^startup/$', startup_redirect),                       
    url(r'^startup/set/$', set_startup, name="add_startup"),
    url(r'^startup/remove/$', set_startup, name="remove_startup", kwargs = {'remove': True }),
    url(r'^favorites/add/$', update_favorites, name="add_favorites"),
    url(r'^favorites/remove/$', update_favorites, name="remove_favorites", kwargs = {'remove': True }),
    url(r'^favorites/remove/profile$', update_favorites, name="profile_remove_fav", kwargs = {'remove': True, 'idtype': True}),
    url(r'^notification/$', mass_notification, name="profile_contact"),
    url(r'^drop-account/$', drop_account, name="drop_account")
)
