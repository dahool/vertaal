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
import traceback, sys

from django.core.management.base import BaseCommand

from django.contrib.auth.models import User
from django.conf import settings
import time
from releases.models import Release
from languages.models import Language
from files.models import POFile, STATUS, LOG_ACTION

import logging
logger = logging.getLogger('vertaal.batch')

class Command(BaseCommand):
    help = 'Set all files from project & team to pending'

    def handle(self, *args, **options):
                
        self.stdout.write('Started.\n')
        logger.info("Start")
        t_start = time.time() 

        BOT_USERNAME = getattr(settings, 'BOT_USERNAME', 'bot')
        BOT_USER = User.objects.get(username=BOT_USERNAME)
            
        # get release
        release = Release.objects.get(slug=args[0])
        lang = Language.objects.get(code=args[1])

        self.stdout.write("Processing %s - %s\n" % (release.name, lang.name))
        
        files = POFile.objects.filter(release=release, language=lang)
        try:
            for pofile in files:
                logger.debug("Processing %s" % pofile.filename)
                pofile.status = STATUS['UNREVIEWED']
                pofile.save()
                pofile.log.create(user=BOT_USER,action=LOG_ACTION['ST_UNREV'])
        except Exception, e:
            logger.error(e.args)
        
        logger.info("End")
        self.stdout.write('Completed in %d seconds.\n' % int(time.time() - t_start))
