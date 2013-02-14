# -*- coding: utf-8 -*-
"""Copyright (c) 2013 Sergio Gabriel Teves
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
from commandlogger import LogBaseCommand
from django.utils.translation import ungettext
from django.contrib.auth.models import User
from django.core.mail import send_mass_mail
from common.i18n import set_user_language
from django.template.loader import render_to_string
from django.conf import settings
import time
import datetime

import logging
logger = logging.getLogger('vertaal.batch')

class Command(LogBaseCommand):
    help = 'Check User Unread Messages'

    def do_handle(self, *args, **options):

        self.stdout.write('Started.\n')
        logger.info("Start")

        meta_diff = datetime.datetime.now() - datetime.timedelta(days=getattr(settings, 'MESSAGE_DAYS_AGE',1))
        
        t_start = time.time() 
        
        mailing = []
        
        #for user in User.objects.filter(pm_inbox__unread=True, pm_inbox__notified__isnull=True, pm_inbox__message__created__lt=meta_diff).distinct():
        for user in User.objects.filter(pm_inbox__unread=True).distinct():
            #messages = user.pm_inbox.filter(unread=True, notified__isnull=True, message__created__lt=meta_diff)
            messages = user.pm_inbox.filter(unread=True)
            count = messages.count()
            logger.debug("There are %s messages for %s" % (count, user))
            set_user_language(user)
            subject = ungettext('You have %(count)d unread message', 'You have %(count)d unread messages', count) % {
                'count': count,
            }
            message = render_to_string('updater/unread_messages.mail', {'message_count': count,
                                                                        'user': user,
                                                                        'messages':  messages.all()})
            mailing.append((subject, message, None, [ user.email ]))
            messages.update(notified=datetime.datetime.now())
       
        if len(mailing)>0:
            logger.debug("Notify %d users" % len(mailing))
            send_mass_mail(mailing, True)
        logger.info("End")
        
        self.stdout.write('Completed in %d seconds. Notified %s.\n' % (int(time.time() - t_start), len(mailing)))
        
        return "Notify %d users" % len(mailing)