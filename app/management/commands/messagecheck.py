# -*- coding: utf-8 -*-
"""Copyright (c) 2012 Sergio Gabriel Teves
All rights reserved.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
from django.core.management.base import BaseCommand
from django.utils.translation import ugettext as _
from django.utils.translation import ungettext
from django.template import loader, Context
from django.contrib.auth.models import User
from django.core.mail import send_mass_mail
from notifications.models import UserMessages
from batch.log import (logger)
from common.i18n import set_user_language
from django.template.loader import render_to_string
from django.db.models.fields import FieldDoesNotExist
from django.conf import settings
import time
import datetime

class Command(BaseCommand):
    help = 'Check User Unread Messages'

    def handle(self, *args, **options):

        self.stdout.write('Started.\n')
        logger.info("Start")

        meta_diff = datetime.datetime.now() - datetime.timedelta(days=getattr(settings, 'MESSAGE_DAYS_AGE',2))
        prefix = getattr(settings,'EMAIL_SUBJECT_PREFIX','')
        NOW = datetime.datetime.now()
        
        t_start = time.time() 
        
        mailing = []
        
        for user in User.objects.all():
            if user.message_set.all():
                try:
                    user.message_set.filter(status__created__lt=meta_diff).delete()
                except:
                    pass
                try:
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
        
        self.stdout.write('Completed in %d seconds.\n' % int(time.time() - t_start))