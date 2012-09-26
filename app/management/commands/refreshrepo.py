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

from django.contrib.auth.models import User
from django.conf import settings
import time
from versioncontrol.manager import Manager, LockRepo
from versioncontrol.models import BuildCache
from batch.log import (logger)
from projects.models import Project

class Command(BaseCommand):
    help = 'Refresh Repositories'

    def handle(self, *args, **options):

        self.stdout.write('Started.\n')
        logger.info("Start")
        t_start = time.time() 

        BOT_USERNAME = getattr(settings, 'BOT_USERNAME', 'bot')
        BOT_USER = User.objects.get(username=BOT_USERNAME)

        projects = Project.objects.filter(enabled=True, read_only=False)
        
        b = None
        failedProjects = []
        try:
            for project in projects:
                teams = project.teams.all()
                for release in project.releases.filter(enabled=True, read_only=False):
                    for component in project.components.all():

                        try:
                            b = BuildCache.objects.get(component=component, release=release)
                            if b.is_locked:
                                break
                        except:
                            b = BuildCache.objects.create(component=component,
                                                      release=release)
                        
                        b.lock()

                        try:
                            for team in teams:
                                if project.slug in failedProjects:
                                    self.stdout.write("Project %s skipped because previous fails\n" % project.slug)
                                    logger.info("Project %s skipped because previous fails" % project.slug)
                                    break
                                
                                logger.info("Refresh project %s, release %s, component %s, team %s" % (project.name,
                                                                                                      release.name,
                                                                                                      component.name,
                                                                                                      team.language.name))
                                man = Manager(project, release, component, team.language, user=BOT_USER)
                                
                                try:
                                    with LockRepo(project.slug,
                                                  release.slug,
                                                  component.slug,
                                                  team.language.code) as lock:        
                                        man.refresh()
                                    man.update_stats(False)
                                except Exception, e:
                                    failedProjects.append(project.slug)
                                    logger.error(e)
                                    traceback.print_exc(file=sys.stdout)
                                finally:
                                    del man
                        finally:
                            if b: b.unlock()
                            
        except Exception, e:
            logger.error(e.args)
            if b: b.unlock()
        logger.info("End")
        
        self.stdout.write('Completed in %d seconds.\n' % int(time.time() - t_start))
