#!/usr/bin/python
import os
import sys

from sqlobject import *
from sqlobject.main import SQLObjectNotFound

PATH = os.path.normpath(os.path.abspath(os.path.dirname(__file__)))
root, path = os.path.split(PATH)
sys.path.append(root)

PROJECT_ID = 1

# django settings setup
from django.core.management import setup_environ

try:
    import settings
except ImportError:
    import sys
    sys.stderr.write("Error: Can't find the file 'settings.py' in the directory containing %r. It appears you've customized things.\nYou'll have to run django-admin.py, passing it your settings module.\n(If the file settings.py does indeed exist, it's causing an ImportError somehow.)\n" % __file__)
    sys.exit(1)

setup_environ(settings)
# -- * --
from django.contrib.auth.models import User, Group
from teams.models import Team

teams = Team.objects.all()

for team in teams:
    print "Processing team %s" % team.pk
    for user in team.coordinators.all():
        try:
            user.groups.add(Group.objects.get(name='Coordinator'))
        except Exception, e:
            print e        

print "Done"