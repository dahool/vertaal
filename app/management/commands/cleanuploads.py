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
from __future__ import with_statement
import traceback, sys, os

from django.core.management.base import BaseCommand

from django.contrib.auth.models import User
from django.conf import settings
import time
import datetime
from versioncontrol.manager import Manager, LockRepo
from versioncontrol.models import BuildCache
from batch.log import (logger)
from projects.models import Project

class Command(BaseCommand):
    help = 'Notify Pending Submits'

    def handle(self, *args, **options):

        self.stdout.write('Started.\n')
        logger.info("Start")
        t_start = time.time() 

        count = 0
        
        CLEAN_AGE = getattr(settings, 'BACKUP_CLEAN_AGE', 15)
        TODAY = datetime.datetime.today()

        logger.debug("Processing project backup ...")
        for dir in os.walk(settings.UPLOAD_PATH):
            pathname, s, files = dir
            for name in files:
                filename = os.path.join(pathname, name)
                logger.debug("Processing %s" % filename)
                if str.lower(os.path.splitext(filename)[-1]) == '.bak':
                    created = datetime.datetime.fromtimestamp(os.stat(filename).st_mtime)
                    diff = TODAY - created
                    logger.debug("File age is: %s" % diff.days)
                    if diff.days > CLEAN_AGE:
                        try:
                            logger.debug("Removing %s" % filename) 
                            os.unlink(filename)
                            count+=1
                        except Exception, e:
                            logger.error(e)
                    else:
                        logger.debug("OK")
    
        logger.debug("Processing user path ...")
        for dir in os.walk(settings.TEMP_UPLOAD_PATH):
            pathname, s, files = dir
            for name in files:
                filename = os.path.join(pathname, name)
                logger.debug("Processing %s" % filename)
                created = datetime.datetime.fromtimestamp(os.stat(filename).st_mtime)
                diff = TODAY - created
                logger.debug("File age is: %s" % diff.days)
                if diff.days > CLEAN_AGE:
                    try:
                        logger.debug("Removing %s" % filename) 
                        os.unlink(filename)
                        count+=1
                    except Exception, e:
                        logger.error(e)
                else:
                    logger.debug("OK")

        logger.info("Removed %d" % count)
        self.stdout.write("Removed %d\n" % count)

        logger.info("End")
        
        self.stdout.write('Completed in %d seconds.\n' % int(time.time() - t_start))