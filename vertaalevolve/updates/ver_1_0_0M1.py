import os.path
from django.contrib.auth.models import Group, Permission

try:
    g = Group.objects.create(name='Coordinator')
    g.permissions.add(
                      Permission.objects.get(codename='add_glossary'),
                      Permission.objects.get(codename='change_glossary')
                      )
except Exception, e:
    print e

PATH = os.path.normpath(os.path.abspath(os.path.dirname(__file__)))

try:
    execfile(os.path.join(PATH,"migv2g","procgroups.py"))
except Exception, e:
    print e