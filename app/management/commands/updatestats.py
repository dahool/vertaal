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
from versioncontrol.manager import Manager, LockRepo, POTUpdater
from versioncontrol.models import BuildCache
from batch.log import (logger)
from projects.models import Project
from files.models import POFile
from django.db.models.signals import pre_save

from common.notification import FileUpdateNotification, POTFileChangeNotification

global notification, potnotification

def init_env():
    global notification, potnotification
    BOT_USERNAME = getattr(settings, 'BOT_USERNAME', 'bot')
    BOT_USER = User.objects.get(username=BOT_USERNAME)

    notification = FileUpdateNotification(BOT_USER, logger)
    potnotification = POTFileChangeNotification(None, logger)

def update_callback(sender, **kwargs):
    global notification
    new = kwargs['instance']
    if new.pk:
        try:
            actual = sender.objects.get(pk=new.pk)
        except Exception, e:
            logger.error(e)
        else:
            notification.check_notification(new, actual)


class Command(BaseCommand):
    help = 'Refresh Repositories And Update Stats'

    def handle(self, *args, **options):
        global notification, potnotification
                
        self.stdout.write('Started.\n')
        logger.info("Start")
        t_start = time.time() 

        init_env()
        
        BOT_USERNAME = getattr(settings, 'BOT_USERNAME', 'bot')
        BOT_USER = User.objects.get(username=BOT_USERNAME)
            
        pre_save.connect(update_callback, sender=POFile)

        projects = Project.objects.filter(enabled=True, read_only=False)
        b = None
        try:
            failedProjects = []
            for project in projects:
                teams = project.teams.all()
                for release in project.releases.filter(enabled=True, read_only=False):
                    for component in project.components.all():
                        b = None
                        try:
                            b = BuildCache.objects.get(component=component, release=release)
                            if b.is_locked:
                                logger.info("Project %s - Component %s - Release %s is LOCKED" % (project.name,
                                                                                                  component.name,
                                                                                                  release.name))
                                break
                            else:
                                b.lock()
                        except BuildCache.DoesNotExist:
                            b = BuildCache.objects.create(component=component,
                                                      release=release)
                            b.lock()
                        except Exception, e:
                            b = None
                            logger.error(e)
                            traceback.print_exc(file=sys.stdout)
                        if b:
                            for team in teams:
                                if project.slug in failedProjects:
                                    self.stdout.write("Project %s skipped because previous fails\n" % project.slug)
                                    logger.info("Project %s skipped because previous fails" % project.slug)
                                    break
                                                                    
                                logger.info("Update project %s, release %s, component %s, team %s" % (project.name,
                                                                                                      release.name,
                                                                                                      component.name,
                                                                                                      team.language.name))
                                man = Manager(project, release, component, team.language, user=BOT_USER)
                                try:
                                    with LockRepo(project.slug,
                                                  release.slug,
                                                  component.slug,
                                                  team.language.code) as lock:        
                                        b.setrev(man.refresh())
                                    man.update_stats(False)
                                except Exception, e:
                                    failedProjects.append(project.slug)
                                    logger.error(e)
                                    traceback.print_exc(file=sys.stdout)
                                finally:
                                    del man
                                
                            if component.potlocation:
                                logger.info("Processing POT")
                                repo = POTUpdater(project, release, component)
                                try:
                                    repo.update_stats(True)
                                except Exception, e:
                                    logger.error(e)
                                    traceback.print_exc(file=sys.stdout)
                                finally:
                                    del repo
                                    
                                filelst = POFile.objects.filter(component=component, release=release)
                                for pofl in filelst:
                                    potnotification.check_notification(pofl, None, True)
                            else:
                                logger.debug("POT skipped")
    
                            b.unlock()
        except Exception, e:
            logger.error(e.args)
            if b: b.unlock()

        pre_save.disconnect(update_callback, sender=POFile)
        
        self.stdout.write("Processing %d notifications " % len(notification.notifications))
        logger.info("Processing %d notifications " % len(notification.notifications))    
        notification.process_notifications()
        self.stdout.write("Processing %d POT notifications " % len(potnotification.notifications))
        logger.info("Processing %d POT notifications " % len(potnotification.notifications))    
        potnotification.process_notifications()
        
        logger.info("End")
        self.stdout.write('Completed in %d seconds.\n' % int(time.time() - t_start))