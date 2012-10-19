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
from commandlogger import LogBaseCommand

from django.utils.translation import ugettext as _
from django.contrib.auth.models import User, Permission
from django.core.mail import send_mass_mail
from common.i18n import set_user_language
from django.template.loader import render_to_string
from django.conf import settings
import time

from teams.models import Team
from files.models import POFileSubmit
from batch.log import (logger)

class Command(LogBaseCommand):
    help = 'Notify Pending Submits'

    def do_handle(self, *args, **options):

        self.stdout.write('Started.\n')
        logger.info("Start")
        t_start = time.time() 
        rsp = None
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
                rsp = "Notify %d users" % len(sendm)
                send_mass_mail(sendm, True)        

        logger.info("End")
        self.stdout.write('Completed in %d seconds.\n' % int(time.time() - t_start))
        
        return rsp