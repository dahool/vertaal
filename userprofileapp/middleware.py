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
from django.utils.cache import patch_vary_headers
from django.utils import translation
from django.conf import settings

class UserLocaleMiddleware(object):
    """
    looks for user language on profile
    """
    def process_request(self, request):
        if request.user.is_authenticated():
            try:
                lang = request.user.profile.get().language    
            except:
                lang = translation.get_language_from_request(request)
            else:
                supported = dict(settings.LANGUAGES)
                if lang not in supported:
                    lang = translation.get_language_from_request(request)
            translation.activate(lang)
        request.LANGUAGE_CODE = translation.get_language()
    
    def process_response(self, request, response):
        patch_vary_headers(response, ('Accept-Language',))
        if 'Content-Language' not in response:
            response['Content-Language'] = translation.get_language()
        translation.deactivate()
        return response
