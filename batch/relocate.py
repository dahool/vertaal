#!/usr/bin/env python
import os
import sys

PATH = os.path.normpath(os.path.abspath(os.path.dirname(__file__)))
root, path = os.path.split(PATH)
sys.path.append(root)

# django settings setup
from django.core.management import setup_environ

try:
    import settings
except ImportError:
    sys.stderr.write("Error: Can't find the file 'settings.py' in the directory containing %r. It appears you've customized things.\nYou'll have to run django-admin.py, passing it your settings module.\n(If the file settings.py does indeed exist, it's causing an ImportError somehow.)\n" % __file__)
    sys.exit(1)

setup_environ(settings)
# -- * --
from files.models import *
from versioncontrol.manager import get_repository_location
from projects.models import Project

def execute():
    projects = Project.objects.filter(enabled=True, read_only=False)
    try:
        for project in projects:
            teams = project.teams.all()
            for release in project.releases.filter(enabled=True, read_only=False):
                for component in project.components.all():
                        for team in teams:
                            location = get_repository_location(project, release, component, team.language)
                            pofile_list = POFile.objects.filter(release=release, component=component, language=team.language)
                            for pofile in pofile_list:
                                if not os.path.normpath(os.path.dirname(pofile.file)) == os.path.normpath(location):
                                     print "Relocate from %s to %s" % (os.path.normpath(os.path.dirname(pofile.file)),
                                                                       os.path.normpath(location))
                                     pofile.file = os.path.join(os.path.normpath(location), os.path.basename(pofile.file))
                                     pofile.save()
    except Exception, e:
        print e
    
if __name__ == '__main__':
    print "Start"
    execute()
    print "End"