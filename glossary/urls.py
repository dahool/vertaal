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

urlpatterns = patterns('glossary.views',
    url(r'^(?P<project>[-\w]+)/(?P<lang>[-_@\w]+)/list/$', 'show_all', name="gloss_list"),
    url(r'^(?P<project>[-\w]+)/(?P<lang>[-_@\w]+)/add/$', 'create_update', name="gloss_add"),
    url(r'^(?P<word_id>[0-9]+)/edit/$', 'create_update', name="gloss_edit"),
    url(r'^(?P<word_id>[0-9]+)/remove/$', 'remove_word', name="gloss_remove"),
    url(r'^(?P<word_id>[0-9]+)/log/$', 'show_log', name="gloss_log"),
    url(r'^select/$', 'language_selection', name="gloss_lang_selection"),
    url(r'^(?P<project>[-\w]+)/(?P<lang>[-_@\w]+)/export/$', 'export_tbx', name="export_tbx"),
    url(r'^$', 'show_all', name="gloss_home"),
)