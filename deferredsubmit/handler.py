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
from __future__ import with_statement
from deferredsubmit.models import POFileSubmitDeferred
from django.conf import settings
from django.utils.encoding import smart_unicode
from versioncontrol.manager import SubmitClient
import traceback

import logging
logger = logging.getLogger('vertaal.deferredsubmit')

deferred_enabled = getattr(settings,'DEFERRED_SUBMIT', False)

def add_submit(filesubmit, user, repo_user, repo_pwd, msg):
    try:
        podef = POFileSubmitDeferred.objects.get(filesubmit=filesubmit)
        podef.repo_user = repo_user
        podef.repo_pwd = repo_pwd
        podef.user = user
        podef.message = msg
        podef.save()
    except POFileSubmitDeferred.DoesNotExist:
        podef = POFileSubmitDeferred.objects.create(filesubmit=filesubmit, user=user, repo_user=repo_user, repo_pwd=repo_pwd, message=msg)
    filesubmit.locked = True
    filesubmit.save()
    
def add_submits(submits, user, repo_user, repo_pwd, msg):
    for submit in submits:
        add_submit(submit, user, repo_user, repo_pwd, msg)

class UserFiles:
    user = None
    repo_user = None
    repo_pwd = None
    files = []
    deffiles = []
    messages = set()
    
    def __init__(self, user, repo_user, repo_pwd):
        self.user = user
        self.repo_user = repo_user
        self.repo_pwd = repo_pwd
    
    def add_message(self, msg):
        if msg and len(msg)>0:
            self.messages.add(msg)
    
    def add_files(self, posubmit, deffile, msg):
        self.files.append(posubmit)
        self.deffiles.append(deffile)
        self.add_message(msg)
        
    @property
    def message(self):
        return "\n".join(self.messages)
        
def process_queue():
    from django.utils.translation import ugettext as _
    from common.utils.lock import LockException
    from common.i18n import UserLanguage
    from django.template.loader import render_to_string
    from django.core.mail import send_mail
    from djangopm.utils import send_pm
    
    count = 0
    erc = 0
    submits = {}
    # group by project and user
    files = POFileSubmitDeferred.objects.get_ordered()
    for sf in files:
        project = sf.filesubmit.pofile.release.project.slug
        userkey = sf.user.username
        if not submits.has_key(project):
            submits[project] = {userkey: UserFiles(sf.user, sf.repo_user, sf.repo_pwd)}
        elif not submits[project].has_key(userkey):
            submits[project][userkey] = UserFiles(sf.user, sf.repo_user, sf.repo_pwd)
        submits[project][userkey].add_files(sf.filesubmit, sf, sf.message)
        sf.lock()
        
    for project in submits.values():
        for userfile in project.values():
            c = SubmitClient(userfile.files,
                             userfile.user,
                             userfile.repo_user,
                             userfile.repo_pwd,
                             userfile.message)
            try:
                count += 1
                c.run(True)
                # if success the file is removed when the fk gets removed.
            except LockException, e:
                logger.error(e)
                for sf in userfile.deffiles: sf.lock(False)
            except Exception, e:
                for sf in userfile.deffiles:
                    try:
                        sf.delete()
                    except Exception:
                        pass
                erc += 1
                logger.error(e)
                logger.error(traceback.format_exc())

                # send mail
                try:
                    with UserLanguage(userfile.user) as user_lang:
                        subject = getattr(settings, 'EMAIL_SUBJECT_PREFIX','') + _("File submit failed")
                        message = render_to_string('updater/commitfail.mail', {'error': smart_unicode(e)})
                        send_mail(subject, message, None, [userfile.user.email])
                except Exception, e:
                    logger.error(str(e))
                
    return {'count': count, 'errors': erc}
