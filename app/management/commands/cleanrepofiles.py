# -*- coding: utf-8 -*-
"""Copyright (c) 2015 Sergio Gabriel Teves
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
from __future__ import with_statement
import traceback, sys

from django.core.management.base import BaseCommand

from django.contrib.auth.models import User
from django.conf import settings
import time
from optparse import make_option
from versioncontrol.manager import get_repository_location
from versioncontrol.models import BuildCache
from projects.models import Project
import shutil
import os

import logging
logger = logging.getLogger('vertaal.batch')

class Command(BaseCommand):
    help = 'Remove files for disabled repositories'
    
    option_list = BaseCommand.option_list
        
    def remove_files(self, path):
        if os.path.exists(path):
            try:
                logger.debug("Remove %s" % path)
                self.stdout.write("Remove %s" % path)
                shutil.rmtree(path)
            except Exception, e:
                logger.error(e.args)
                traceback.print_exc(file=sys.stdout)
                
    def handle(self, *args, **options):

        self.stdout.write('Started.\n')
        logger.info("Start")
        t_start = time.time() 
        
        projects = Project.objects.all()
        for project in projects:
            if project.enabled == False:
                project_path = get_repository_location(project)
                self.remove_files(project_path)
            else:
                for release in project.releases.filter(enabled=False):
                    release_path = get_repository_location(project, release)
                    self.remove_files(release_path)
                            
        logger.info("End")
        
        self.stdout.write('Completed in %d seconds.\n' % int(time.time() - t_start))
