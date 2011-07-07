#!/usr/bin/python
import os
import sys

from sqlobject import *
from sqlobject.main import SQLObjectNotFound

"""
FIX: eliminar caracteres incorrectos de los nombres
validar direcciones de mail duplicadas
"""

PATH = os.path.normpath(os.path.abspath(os.path.dirname(__file__)))
root, path = os.path.split(PATH)
sys.path.append(root)

PROJECT_ID = 1

class V2GTeam(SQLObject):
    class sqlmeta:
        table = 'teams'
        idName = 'id'
        
    lang = StringCol()
    status = StringCol()
    
class V2GUser(SQLObject):
    class sqlmeta:
        table = 'users'
        idName = 'userid'
        idType = str
    
    mail = StringCol()
    password = StringCol()
    groupid = StringCol()
    status = StringCol()
    name = StringCol()
    team = ForeignKey('V2GTeam', dbName='teamid')

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
from django.contrib.auth.models import User, Permission
from teams.models import Team
from projects.models import Project
from languages.models import Language
from django.db import IntegrityError
from django.db import transaction

MySQLConnection = mysql.builder()
conn = MySQLConnection(host=settings.V2G_DB_HOST, user=settings.V2G_DB_USER, password=settings.V2G_DB_PWD, db=settings.V2G_DB_NAME)
sqlhub.processConnection = conn

v = V2GUser.select(V2GUser.q.status=="ACTIVE")

project = Project.objects.get(id=PROJECT_ID)
permission = Permission.objects.get(codename='can_commit')

transaction.enter_transaction_management()
transaction.managed(True)

for u in list(v):
    print "Creating %s" % u.id
    try:
        user = User(username=u.id, email=u.mail)
        user.password = 'sha1$$%s' % u.password
        if u.groupid == 'ADMIN':
            user.is_staff = True
            user.is_superuser = True
        user.save()            
        team = None
        try:
            ul = u.team.lang
        except SQLObjectNotFound:
            pass
        else:
            try:
                print "Looking for team %s" % u.team.lang
                team = Team.objects.get(project=project, language__code__iexact=u.team.lang)
            except:
                print "Team not found. Go for language"
                try:
                    lang = Language.objects.get(code__iexact=u.team.lang)
                except:
                    print "Language %s not found!?" % u.team.lang
                else:
                    print "Creating team for %s" % lang.name
                    team = Team.objects.create(project=project, language=lang)
            else:
                pass
            if team:
                if u.groupid == 'COORD':
                    print "Add %s as Coordinator" % u.id
                    team.coordinators.add(user)
                else:
                    print "Add %s as Member" % u.id
                    team.members.add(user)
                    if u.groupid == 'SVN':
                        print "Add submit grants"
                        user.user_permissions.add(permission)

    except IntegrityError, e:
        #print "Duplicated user %s" % u.id
        transaction.rollback()
        print e.args
    else:
        transaction.commit()
        
transaction.leave_transaction_management()

print "Done"
conn.close()