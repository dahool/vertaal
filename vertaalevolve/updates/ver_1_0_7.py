#!/usr/bin/python

from sqlobject import *
from sqlobject.main import SQLObjectNotFound

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
    userid = StringCol()
    team = ForeignKey('V2GTeam', dbName='teamid')

from projects.models import Project
from languages.models import Language
from glossary.models import Glossary
from django.db import IntegrityError
from django.db import transaction
from django.contrib.auth.models import User

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
            try:
                g = Glossary.objects.get(word__iexact=term.english_term,
                                         language=lang,
                                         project=project)
            except Glossary.DoesNotExist:
                print "Term %s not exists. Error?" % term.english_term
            except Exception, e:
                print e       
            else:
                uname = term.userid
                try:
                    u = User.objects.get(username=uname.replace(' ','_'))
                except:
                    print "User %s not exists" % uname
                else:
                    if g.history.all():
                        x = g.history.create(user=u,
                                         translation=g.translation,
                                         action_flag='C')
                        x.created=term.lastupdate
                        x.save()                        
                    else:
                        x = g.history.create(user=u,
                                         translation=g.translation,
                                         action_flag='A')
                        x.created=term.lastupdate
                        x.save()
                    
    except IntegrityError, e:
        transaction.rollback()
        print e
    else:
        transaction.commit()
        
transaction.leave_transaction_management()

print "Done"
conn.close()