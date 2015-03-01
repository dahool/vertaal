# -*- coding: utf-8 -*-
"""Copyright (c) 2013 Sergio Gabriel Teves
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
import datetime
from django import template
from django.utils import formats
from django.utils.dateformat import format
from django.conf import settings

from django.utils.translation import ungettext, gettext

register = template.Library()

TIME_FORMAT = getattr(settings, 'PM_DATE_FORMAT', 'H:i')
DATE_FORMAT = getattr(settings, 'PM_DATE_FORMAT', 'M d' )
DATE_FORMAT_LONG = getattr(settings, 'PM_DATE_FORMAT', 'M d, Y')

@register.filter(is_safe=False)
def date_todaytime(value):
    fmt = None
    today = datetime.date.today()
    if value.date() < today:
        if value.date().year < today.year:
            fmt = DATE_FORMAT_LONG
        else:
            fmt = DATE_FORMAT
    else:
        fmt = TIME_FORMAT
    try:
        return formats.date_format(value, fmt)
    except AttributeError:
        try:
            return format(value, fmt)
        except AttributeError:
            return ''
        
@register.inclusion_tag('djangopm/pmcount_tag.html', takes_context=True)
def pmcount(context):
    user = context['user']
    count = user.pm_inbox.unread().count()
    if count > 0:
        title = ungettext(
            'You have %(count)d unread message',
            'You have %(count)d unread messages',
        count) % {
            'count': count,
        } 
    else:
        title = gettext("Private Messages")
    return {'count': count, 'title': title}