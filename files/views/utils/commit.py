# -*- coding: utf-8 -*-
"""Copyright (c) 2013, Sergio Gabriel Teves
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
import traceback
import logging

from django.utils.translation import ungettext, ugettext as _
from django.contrib import messages
from django.utils.encoding import smart_unicode

from deferredsubmit import handler as deferredhandler
from versioncontrol.manager import SubmitClient

logger = logging.getLogger(__name__)

def do_commit(request, submits, user, repo_user, repo_pass, message=''):
    if deferredhandler.deferred_enabled:
        deferredhandler.add_submits(submits, user, repo_user, repo_pass, message)
        msg = ungettext('The file was added to the queue for further processing.',
                            'The files were added to the queue for further processing.', len(submits))
        messages.info(request, message=msg)
    else:
        c = SubmitClient(submits,
                         user,
                         repo_user,
                         repo_pass,
                         message)
        try:
            c.run()
            msg = ungettext('File submitted.',
                            'Files submitted.', len(submits))          
            messages.success(request, message=msg)
        except Exception, e:
            logger.error(e)
            logger.error(traceback.format_exc())
            messages.error(request, message=_("Failed. Reason: %s") % smart_unicode(e))
            return False
    return True