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
from django import template
from django.conf import settings
from django.utils.encoding import force_unicode
from news.models import Article

register = template.Library()

@register.inclusion_tag('news/latest.html', takes_context=True)
def latest_news(context):
    return {'news': Article.objects.all_active().order_by("-created")[:getattr(settings, 'LATEST_NEWS',10)],
			'user': context['user'],
			'perms': context['perms']}