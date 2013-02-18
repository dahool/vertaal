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
from django.conf.urls import patterns, url

urlpatterns = patterns('files.views.filelist',
    url(r'^(?P<release>[-\w]+)/(?P<language>[-_@\w]+)/list/$', 'list_files', name="list_files"),
    url(r'^(?P<release>[-\w]+)/(?P<language>[-_@\w]+)/list/reload/$', 'list_files', name="reload_list_files", kwargs = {'filter': True }),
    url(r'^(?P<release>[-\w]+)/(?P<language>[-_@\w]+)/(?P<component>[-_@\w]+)/list/$', 'list_files', name="list_files_component", kwargs = {'filter': True }),
    url(r'^(?P<slug>[-\w]+)/detail/toggle/$', 'toggle', name="toggle_lock_detail", kwargs={'template': 'files/file_detail_status.html'}),
    url(r'^(?P<slug>[-\w]+)/detail/$', 'file_detail', name="file_detail"),
    url(r'^(?P<slug>[-\w]+)/toggle/$', 'toggle', name="toggle_lock"),
    url(r'^(?P<slug>[-\w]+)/toggle_mark/$', 'toggle_mark', name="toggle_mark"),
    url(r'^(?P<slug>[-\w]+)/toggle_translator/set/$', 'toggle_assigned', name="set_assigned_translator", kwargs = {'translator': True}),
    url(r'^(?P<slug>[-\w]+)/toggle_reviewer/set/$', 'toggle_assigned', name="set_assigned_reviewer", kwargs = {'translator': False}),    
    url(r'^(?P<slug>[-\w]+)/toggle_translator/remove/$', 'toggle_assigned', name="remove_assigned_translator", kwargs = {'remove': True, 'translator': True}),
    url(r'^(?P<slug>[-\w]+)/toggle_reviewer/remove/$', 'toggle_assigned', name="remove_assigned_reviewer", kwargs = {'remove': True, 'translator': False}),
    url(r'^(?P<slug>[-\w]+)/log/$', 'file_log', name="file_log"),
    url(r'^$', 'list_files', name="files_home"),
)

urlpatterns += patterns('files.views.filehandling',
    url(r'^(?P<slug>[-\w]+)/get/$', 'get_file', name="get_file"),
    url(r'^(?P<slug>[-\w]+)/pot/$', 'get_pot_file', name="get_pot_file"),
    url(r'^(?P<slug>[-\w]+)/s-get/$', 'get_file', name="get_submit_file", kwargs = {'submit': True }),
    url(r'^(?P<id>[\d]+)/s-get-arch/$', 'get_file_arch', name="get_submit_file_arch"),
    url(r'^(?P<slug>[-\w]+)/view/$', 'get_file', name="view_file", kwargs = {'view': True }),
    url(r'^(?P<slug>[-\w]+)/s-view/$', 'get_file', name="view_submit_file", kwargs = {'view': True , 'submit': True}),
    url(r'^(?P<slug>[-\w]+)/edit/$', 'edit_file', name="edit_file"),
    url(r'^(?P<slug>[-\w]+)/s-edit/$', 'edit_submit_file', name="edit_submit_file"),
    url(r'^(?P<slug>[-\w]+)/merge/$', 'do_merge', name="file_merge"),                       
)
    
urlpatterns += patterns('files.views.filediff',
    url(r'^(?P<slug>[-\w]+)/diff/$', 'view_file_diff', name="view_file_diff"),
    url(r'^(?P<slug>[-\w]+)/udiff/$', 'view_file_diff', name="view_file_udiff", kwargs = {'uniff': True}),                 
)

urlpatterns += patterns('files.views.filesubmit',
    url(r'^(?P<release>[-\w]+)/(?P<language>[-_@\w]+)/put/$', 'upload', name="file_upload"),
    url(r'^(?P<slug>[-\w]+)/s-upload/$', 'submit_new_file', name="submit_new_file"),
    url(r'^(?P<team>[-\w]+)/submit/$', 'submit_team_file', name="file_submit"),
    url(r'^qsubmit/$', 'submit_team_file', name="file_qsubmit"),
    url(r'^confirm/$', 'confirm_submit', name="confirm_submit"),
    url(r'^commit_queue/$', 'commit_queue', name="commit_queue"),
    url(r'^(?P<team>[-\w]+)/reject/$', 'submit_team_file', name="file_reject", kwargs = {'reject': True }),
)
