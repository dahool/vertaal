import os
import sys

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
from django.contrib.auth.models import User
from django.core.mail import send_mass_mail
from batch.log import (logger)

def execute():
    users = User.objects.all()
    prefix = getattr(settings,'EMAIL_SUBJECT_PREFIX','')
    mailing = []
    logger.info("Start")
    for user in users:
        if user.message_set.all():
            count = user.message_set.all().count()
            subject = ungettext('You have %(count)d unread message', 'You have %(count)d unread messages', count) % {
                'count': count,
            }            
            message = loader.get_template('updater/unread_messages.mail').render(
                                Context({'message_count': count}))
            mailing.append((subject, message, None, [ user.email ]))

    if len(mailing)>0:
        logger.debug("Notify %d users" % len(mailing))
        send_mass_mail(mailing, True)
    logger.info("End")

if __name__ == '__main__':
    print "Start"
    execute()
    print "End"