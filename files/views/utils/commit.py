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
import threading

from django.utils.translation import ungettext, ugettext as _
from django.contrib import messages
from django.utils.encoding import smart_unicode

from deferredsubmit import handler as deferredhandler
from versioncontrol.manager import SubmitClient, SubmitException
from django.conf import settings

import logging
logger = logging.getLogger('vertaal.files')

def __perform_commit(**kw):
    request = kw.pop('request',None)
    c = SubmitClient(**kw)
    try:
        c.run()
        msg = ungettext('File submitted.',
                        'Files submitted.', len(submits))
        if request is not None:
            messages.success(request, message=msg)
    except SubmitException, se:
        logger.error(se)
        if request is not None:
            messages.error(request, message=_("Submit failed. Reason: %s") % smart_unicode(e))
        else:
            if len(se.files) > 0 and deferredhandler.deferred_running:
                logger.info("%d files added to deferred handler because they were locked at this moment" % len(se.files))
                deferredhandler.add_submits(se.files, user, repo_user, repo_pass, message)
            else:
                kw['user'].email_user("Submit failed", message=smart_unicode(e))
        return False
    except Exception, e:
        logger.error(e)
        logger.error(traceback.format_exc())
        if request is not None:
            messages.error(request, message=_("Submit failed. Reason: %s") % smart_unicode(e))
        else:
            kw['user'].email_user("Submit failed", message=smart_unicode(e))
        return False
    return True
    
def do_commit(request, submits, user, repo_user, repo_pass, message=''):
    if deferredhandler.deferred_enabled:
        deferredhandler.add_submits(submits, user, repo_user, repo_pass, message)
        msg = ungettext('File added to the queue for further processing.',
                            'Files added to the queue for further processing.', len(submits))
        messages.info(request, message=msg)
    else:
        args = {'files': submits,
                'current_user': user,
                'user': repo_user,
                'pword': repo_pass,
                'message': message}

        if getattr(settings, 'SUBMIT_OFFLINE', False) is True:
            t = threading.Thread(target=__perform_commit,
                         name="commit_%s" % user.username,
                         kwargs=args)
            t.start()
            msg = ungettext("The file is being processed. You'll be notified once completed.",
                                "The files are being processed. You'll be notified once completed.", len(submits))
            messages.info(request, message=msg)            
        else:
            args['request'] = request
            return __perform_commit(args)
    return True