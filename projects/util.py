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
import os
from django.conf import settings

from django.contrib import messages
from django.utils.translation import ugettext as _

def check_project(request, project):
    if not project.enabled:
        if project.is_maintainer(request.user):
            messages.warning(request, message=_('This project is disabled. Only maintainers can view it.'))
            return True
        else:
            return False
    return True
    
def get_build_log_file(project_slug,
                  release_slug):

    BUILD_LOG_PATH = getattr(settings, 'BUILD_LOG_PATH')    
    
    if not os.path.exists(BUILD_LOG_PATH):
        os.makedirs(BUILD_LOG_PATH)
    
    logfile = os.path.join(BUILD_LOG_PATH,
                                "_".join([project_slug, 
                                          release_slug])) + '.log'
    
    return logfile