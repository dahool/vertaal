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
from languages.models import Language
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView

urlpatterns = patterns('',
    url(r'^(?P<slug>[-_@\w]+)/$', DetailView.as_view(
                                queryset=Language.objects.all(), 
                                slug_field='code',
                                context_object_name='language', 
                                template_name='languages/language_detail.html'),
        name = 'language_detail'),                       
    url(r'^$', ListView.as_view(
                                queryset=Language.objects.all(), 
                                context_object_name='language_list', 
                                template_name='languages/language_list.html'),
        name = 'language_list'),
)