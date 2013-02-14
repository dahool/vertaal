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
from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('releases.views',
    url(r'^(?P<project>[-\w]+)/add/$', 'release_create_update', name = 'release_create'),
    url(r'^(?P<slug>[-\w]+)/edit/$', 'release_create_update', name = 'release_edit',),
    url(r'^(?P<slug>[-\w]+)/delete/$', 'release_delete', name = 'release_delete',),
    url(r'^(?P<slug>[-\w]+)/populate/$', 'release_populate', name = 'release_populate',),
    url(r'^(?P<slug>[-\w]+)/merge/$', 'multimerge', name = 'multimerge',),
    url(r'^(?P<slug>[-\w]+)/$', 'release_detail', name = 'release_detail',),
    url(r'^(?P<project>[-\w]+)/(?P<release>[-\w]+)/log/$', 'build_log', name = 'build_log',),        
)