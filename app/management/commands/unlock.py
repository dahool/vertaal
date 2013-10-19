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
import traceback, sys

from django.core.management.base import BaseCommand

import time
from versioncontrol.manager import LockRepo
from versioncontrol.models import BuildCache

import logging
logger = logging.getLogger('vertaal.batch')

class Command(BaseCommand):
    help = 'Unloack Repositories'
        
    def handle(self, *args, **options):

        self.stdout.write('Started.\n')
        logger.info("Start")
        t_start = time.time() 

        builds = BuildCache.objects.all()
        
        try:
            for bc in builds:
                if bc.locked:
                    bc.unlock(True)
                teams = bc.release.project.teams.all()                    
                for team in teams:
                    lk = LockRepo(bc.release.project.slug, bc.release.slug, bc.component.slug, team.language.code)
                    lk.is_locked = True
                    lk.release()
        except Exception, e:
            logger.error(e.args)
            traceback.print_exc(file=sys.stdout)
        logger.info("End")
        
        self.stdout.write('Completed in %d seconds.\n' % int(time.time() - t_start))
