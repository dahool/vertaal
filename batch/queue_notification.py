import os
import sys

print "This module is deprecated. Use: manage submitqueuenotifiy instead"
sys.exit(1)

PATH = os.path.normpath(os.path.abspath(os.path.dirname(__file__)))
root, path = os.path.split(PATH)
sys.path.append(root)

try:
    execfile(os.path.join(PATH,'setupenv.py'))
except IOError:
    pass

from django.utils.translation import ugettext as _
from django.template import loader, Context
from django.template.loader import render_to_string
from django.contrib.auth.models import User, Permission
from django.core.mail import send_mass_mail
from django.db import connection
from teams.models import Team
from files.models import POFileSubmit
from batch.log import (logger)

from common.i18n import set_user_language

def execute():
    perm = Permission.objects.get(codename='can_commit')
    prefix = getattr(settings,'EMAIL_SUBJECT_PREFIX','')    
    for team in Team.objects.all():
        logger.debug(team)
        submits = POFileSubmit.objects.by_project_and_language(team.project,
                                                               team.language)
        logger.debug("Count %d" % submits.count())
        if submits.count()>0:
            users = team.coordinators.all()
            ulist = User.objects.filter(id__in=[u.id for u in team.members.all()],
                                        user_permissions=perm,
                                        is_superuser=False)
            # I dont want users see other addresses
            sendm = []
            userlist = list(users)
            userlist.extend(list(ulist))
            for u in userlist:
                set_user_language(u)
                subject = prefix + _("Submission queue status report for %(project)s - %(team)s" % 
                           {'project': team.project.name, 'team': team.language.name})
                message = render_to_string('updater/queuestatus.mail', {'files': submits})
                sendm.append((subject, message, None, [ u.email ]))
                
            logger.debug("Notify %d users" % len(sendm))
            send_mass_mail(sendm, True)

if __name__ == '__main__':
    print "Start"
    execute()
    print "End"