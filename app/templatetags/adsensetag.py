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
from django import template
from django.template import Node, NodeList, VariableDoesNotExist, resolve_variable

register = template.Library()

@register.filter
def adsensecookie(path):
    return 'adsense%s' % path.replace('/','_')

@register.tag
def ifadsensecookie(parser, token):
    end_tag = 'end' + token.split_contents()[0]
    nodelist_true = parser.parse(('else', end_tag))
    token = parser.next_token()
    if token.contents == 'else':
        nodelist_false = parser.parse((end_tag,))
        parser.delete_first_token()
    else:
        nodelist_false = NodeList()
    return IfAdsenseCookieNode(nodelist_true, nodelist_false)

class IfAdsenseCookieNode(Node):
    def __init__(self, nodelist_true, nodelist_false):
        self.nodelist_true, self.nodelist_false = nodelist_true, nodelist_false

    def __repr__(self):
        return "<IfAdsenseCookieNode>"

    def render(self, context):
        try:
            path = resolve_variable('request.path', context)
            cookies = resolve_variable('request.COOKIES', context)
        except VariableDoesNotExist:
            return
        key = adsensecookie(path)
        if cookies.get(key):
            return self.nodelist_true.render(context)
        else:
            return self.nodelist_false.render(context)