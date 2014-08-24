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
import os

from commandlogger import LogBaseCommand

from django.conf import settings
import time
import datetime
from files.models import POFileSubmit, POFileSubmitSet

from django.utils.encoding import smart_unicode

import logging
logger = logging.getLogger('vertaal.batch')

class Command(LogBaseCommand):
    help = 'Notify Pending Submits'

    def do_handle(self, *args, **options):

        self.stdout.write('Started.\n')
        logger.info("Start")
        t_start = time.time() 

        count = 0
        
        CLEAN_AGE = getattr(settings, 'BACKUP_CLEAN_AGE', 15)
        TODAY = datetime.datetime.today()
        AGE_DELTA = TODAY - datetime.timedelta(days=CLEAN_AGE)
        
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
        for dirn in os.walk(settings.TEMP_UPLOAD_PATH):
            pathname, s, files = dirn
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

        count = 0
        logger.debug("Clean orphaned submits ...")
        for fsub in POFileSubmit.objects.all():
            filename = smart_unicode(fsub.file)
            if not os.path.exists(filename):
                fsub.delete()
                count+=1
        
        logger.debug("Clean stalled submits ...")
        for fsub in POFileSubmitSet.objects.filter(created__lt=AGE_DELTA):
            fsub.delete()
            
        logger.info("Removed %d orphaned submits" % count)
        self.stdout.write("Removed %d orphaned submits\n" % count)
        
        logger.info("End")
        
        self.stdout.write('Completed in %d seconds.\n' % int(time.time() - t_start))
        
        return "Removed %d\n" % count