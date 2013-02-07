import os
from django.conf import settings
import logging

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