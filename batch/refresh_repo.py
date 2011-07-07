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
from django.template import loader, Context
from django.db.models.signals import pre_save
from django.core.mail import send_mass_mail
from django.contrib.auth.models import User
from projects.models import Project
from teams.models import Team
from files.models import *
from batch.log import (logger)
from versioncontrol.manager import Manager, LockRepo
from versioncontrol.models import BuildCache

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
                    try:
                        b = BuildCache.objects.get(component=component, release=release)
                        if b.is_locked:
                            break
                        else:
                            b.lock()
                    except:
                        b = BuildCache.objects.create(component=component,
                                                  release=release)
                        b.lock()              
                    else:                        
                        for team in teams:
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
                                logger.error(e)
                                traceback.print_exc(file=sys.stdout)
                            finally:
                                del man
                    finally:
                        if b: b.unlock()
    except Exception, e:
        logger.error(e.args)
        if b: b.unlock()
    
    logger.info("end")
    
if __name__ == '__main__':
    print "Start"
    execute()
    print "End"
