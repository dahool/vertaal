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
import traceback
from django.conf import settings
from exceptionlogger.models import ExceptionLog

import logging
logger = logging.getLogger('exceptionlogger')

class ExceptionLoggerMiddleware(object):
         
    def process_exception(self, request, exception):
        try:
            message = 'EXCEPTION:\n%(exep)s\n\nSTACKTRACE:\n%(trace)s\n\nREQUEST:\n%(request)s' % {'request': str(request), 'exep': str(exception), 'trace': traceback.format_exc()}
            logger.error(message, exc_info=exception)
            if getattr(settings, 'LOG_EXCEPTION_DB', False):
                ExceptionLog.objects.create(request=str(request),
                                            exception=str(exception),
                                            stacktrace=traceback.format_exc())
        except:
            logger.error("Cannot generate error message");
        return None