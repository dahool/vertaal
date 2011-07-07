#!/usr/bin/env python
from __future__ import with_statement
import os
import sys, traceback

PATH = os.path.normpath(os.path.abspath(os.path.dirname(__file__)))
root, path = os.path.split(PATH)
sys.path.append(root)

try:
    execfile(os.path.join(PATH,'setupenv.py'))
except IOError:
    pass

from django.utils.translation import ugettext as _
from django.utils.encoding import smart_unicode
from django.template import loader, Context
from django.template.loader import render_to_string
from django.db.models.signals import pre_save
from django.core.mail import send_mass_mail
from django.contrib.auth.models import User
from projects.models import Project
from teams.models import Team
from files.models import *
from batch.log import (logger)
from versioncontrol.manager import Manager, LockRepo, POTUpdater
from versioncontrol.models import BuildCache
from common.notification import FileUpdateNotification, POTFileChangeNotification

from common.i18n import set_user_language

BOT_USERNAME = getattr(settings, 'BOT_USERNAME', 'bot')
BOT_USER = User.objects.get(username=BOT_USERNAME)

def execute():
    projects = Project.objects.filter(enabled=True, read_only=False)
    logger.info("init")
    b = None
    try:
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
    logger.info("end")
    
def update_callback(sender, **kwargs):
    new = kwargs['instance']
    if new.pk:
        try:
            actual = sender.objects.get(pk=new.pk)
        except Exception, e:
            logger.error(e)
        else:
            notification.check_notification(new, actual)
                            
pre_save.connect(update_callback, sender=POFile)

if __name__ == '__main__':
    print "Start"
    notification = FileUpdateNotification(BOT_USER, logger)
    potnotification = POTFileChangeNotification(None, logger)
    execute()
    pre_save.disconnect(update_callback, sender=POFile)
    print "Processing %d notifications " % len(notification.notifications)
    logger.info("Processing %d notifications " % len(notification.notifications))    
    notification.process_notifications()
    print "Processing %d POT notifications " % len(potnotification.notifications)
    logger.info("Processing %d POT notifications " % len(potnotification.notifications))    
    potnotification.process_notifications()
    print "End"
