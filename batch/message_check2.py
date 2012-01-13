import os
import sys
import datetime

print "This module is deprecated. Use: manage messagecheck instead"
sys.exit(1)

PATH = os.path.normpath(os.path.abspath(os.path.dirname(__file__)))
root, path = os.path.split(PATH)
sys.path.append(root)

try:
    execfile(os.path.join(PATH,'setupenv.py'))
except IOError:
    pass

from django.utils.translation import ugettext as _
from django.utils.translation import ungettext
from django.template import loader, Context
from django.template.loader import render_to_string
from django.contrib.auth.models import User
from django.db.models.fields import FieldDoesNotExist
from django.core.mail import send_mass_mail
from django.db.models import Q
from notifications.models import UserMessages
from batch.log import (logger)

from common.i18n import set_user_language

meta_diff = datetime.datetime.now() - datetime.timedelta(days=getattr(settings, 'MESSAGE_DAYS_AGE',2))
NOW = datetime.datetime.now()

def execute():
    users = User.objects.all()
    prefix = getattr(settings,'EMAIL_SUBJECT_PREFIX','')
    mailing = []
    logger.info("Start")
    for user in users:
        if user.message_set.all():
            try:
                user.message_set.filter(status__created__lt=meta_diff).delete()
            except:
                pass
            try:
#                mlist = user.message_set.filter(
#                                           Q(status__notified__isnull=True) 
#                                           | Q(status__notified__lt=meta_diff))
                mlist = user.message_set.filter(status__notified__isnull=True)
                if mlist:
                    logger.debug("There are messages for %s" % user)
                    for m in user.message_set.all():
                        if m.status.all():
                            s = m.status.get()
                        else:
                            # to avoid two sql calls
                            s = UserMessages(message=m)
                        s.notified=NOW
                        s.save()
                    count = user.message_set.all().count()
                    set_user_language(user)
                    subject = ungettext('You have %(count)d unread message', 'You have %(count)d unread messages', count) % {
                        'count': count,
                    }            
                    message = render_to_string('updater/unread_messages.mail', {'message_count': count,
                                                                                'user': user,
                                                                                'messages': mlist})
                    mailing.append((subject, message, None, [ user.email ]))
                else:
                    logger.debug("No messages for %s" % user)
            except FieldDoesNotExist, e:
                # we should repair this for future lookups
                logger.debug("Create message status")
                for m in user.message_set.filter(status__isnull=True):
                    m.status.create() 

    if len(mailing)>0:
        logger.debug("Notify %d users" % len(mailing))
        send_mass_mail(mailing, True)
    logger.info("End")

if __name__ == '__main__':
    print "Start"
    execute()
    print "End"