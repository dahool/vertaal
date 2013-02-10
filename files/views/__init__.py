# -*- coding: utf-8 -*-
"""Copyright (c) 2013, Sergio Gabriel Teves
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

from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.contrib import messages

from common.middleware.exceptions import Http403
from releases.models import Release
from files.models import POFile

class ResponseMessage:
    
    @staticmethod        
    def info(message):
        return ResponseMessage.get_message(message, 'notice')

    @staticmethod
    def warn(message):
        return ResponseMessage.get_message(message, 'warning')

    @staticmethod
    def error(message):
        return ResponseMessage.get_message(message, 'error')
    
    @staticmethod
    def success(message):
        return ResponseMessage.get_message(message, 'success')

    @staticmethod        
    def get_message(message, message_type):
        return {'text': message, 'type': message_type}
        
        
def escape(text):
    return text.replace("<", "&lt;").replace(">","&gt;")

def check_status(fn):
    """check if the project is enabled"""
    def status_fn(self, *args, **kw):
        request = kw.get('request')
        if kw.has_key('release'):
            release = get_object_or_404(Release,slug=kw['release'])
        elif kw.has_key('slug'):
            pofile = get_object_or_404(POFile,slug=kw['slug'])
            release = pofile.release
        else:
            raise Http404
        if not release.enabled or not release.project.enabled:
            if release.project.is_maintainer(self.user):
                if not release.project.enabled:
                    messages.warning(request, _("This project is disabled. You shouldn't change anything here."))
                else:
                    messages.warning(request, _("This release is disabled. You shouldn't change anything here."))
            else:
                raise Http403
        return fn(self, *args, **kw)
    return status_fn 