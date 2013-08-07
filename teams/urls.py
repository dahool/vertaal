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

urlpatterns = patterns('teams.views',
    url(r'^add-member/(?P<teamid>[-\w]+)/$',
        'add_member',
        name="add_member"),
    url(r'^remove-member/(?P<teamid>[-\w]+)/(?P<userid>[\w.@+-]+)/$',
        'remove_member',
        name="remove_member"),
    url(r'^change-group/(?P<teamid>[-\w]+)/(?P<userid>[\w.@+-]+)/(?P<group>[-\w]+)/$',
        'update_group',
        name="change_group"),
    url(r'^remove-grant/(?P<teamid>[-\w]+)/(?P<userid>[\w.@+-]+)/(?P<codename>[-\w]+)/$',
        'update_permission',
        name="remove_grant",  kwargs = {'remove': True }),
    url(r'^add-grant/(?P<teamid>[-\w]+)/(?P<userid>[\w.@+-]+)/(?P<codename>[-\w]+)/$',
        'update_permission',
        name="add_grant"),
    url(r'^(?P<teamid>[-\w]+)/join/$',
        'join_request',
        name = 'join_request',),
    url(r'^(?P<id>[-\w]+)/join-acccept/$',
        'join_accept',
        name = 'join_accept',),
    url('^(?P<id>[-\w]+)/join-reject/$',
        'join_accept',
        name = 'join_reject',
        kwargs = {'reject': True }),                
    url(r'^(?P<id>[-\w]+)/admin/$',
        'team_admin',
        name = 'team_admin',),
    url(r'^(?P<id>[-\w]+)/contact/$',
        'team_contact',
        name = 'team_contact',),        
    url(r'^(?P<project>[-\w]+)/(?P<lang>[-_@\w]+)/$',
        'team_detail',
        name = 'team_detail',),
    url(r'^(?P<project>[-\w]+)/$',
        'add_team',
        name = 'team_create',),
    url(r'^(?P<project>[-\w]+)/(?P<lang>[-_@\w]+)/remove/$',
        'team_delete',
        name = 'team_remove',)                               
)