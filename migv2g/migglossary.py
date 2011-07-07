#!/usr/bin/python
import os
import sys

from sqlobject import *
from sqlobject.main import SQLObjectNotFound

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
    
class V2GGloss(SQLObject):
    class sqlmeta:
        table = 'glossary'
        idName = 'id'
    
    english_term = StringCol()
    translation = StringCol()
    comments = StringCol()
    lastupdate = DateTimeCol()
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
from projects.models import Project
from languages.models import Language
from glossary.models import Glossary
from django.db import IntegrityError
from django.db import transaction

MySQLConnection = mysql.builder()
conn = MySQLConnection(host=settings.V2G_DB_HOST, user=settings.V2G_DB_USER, password=settings.V2G_DB_PWD, db=settings.V2G_DB_NAME)
sqlhub.processConnection = conn

terms = V2GGloss.select()

project = Project.objects.get(id=PROJECT_ID)

transaction.enter_transaction_management()
transaction.managed(True)

for term in list(terms):
    print "Processing %s" % term.id
    try:
        print "Looking for language %s" % term.team.lang
        try:
            lang = Language.objects.get(code__iexact=term.team.lang)
        except:
            print "Language %s not found!?" % term.team.lang
        else:
            print "Check if already exists %s" % term.english_term
            try:
                g = Glossary.objects.get(word__iexact=term.english_term,
                                         language=lang,
                                         project=project)
            except Glossary.DoesNotExist:
                print "Creating"
                Glossary.objects.create(word=term.english_term,
                                        translation=term.translation,
                                        project=project,
                                        language=lang,
                                        comment=term.comments)
            except Exception, e:
                print e       
            else:
                print "Already exists. Appending"
                g.translation = g.translation + ", " + term.translation
                g.save()

    except IntegrityError, e:
        transaction.rollback()
        print e
    else:
        transaction.commit()
        
transaction.leave_transaction_management()

print "Done"
conn.close()