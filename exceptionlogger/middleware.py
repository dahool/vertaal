import traceback
from django.conf import settings
from exceptionlogger.models import ExceptionLog

import logging
logger = logging.getLogger('exceptionlogger')

class ExceptionLoggerMiddleware(object):
         
    def process_exception(self, request, exception):
        try:
            message = 'EXCEPTION:\n%(exep)s\n\nSTACKTRACE:\n%(trace)s\n\nREQUEST:\n%(request)s' % {'request': str(request), 'exep': str(exception), 'trace': traceback.format_exc()}
            logger.error(message)
            if getattr(settings, 'LOG_EXCEPTION_DB', False):
                ExceptionLog.objects.create(request=str(request),
                                            exception=str(exception),
                                            stacktrace=traceback.format_exc())
        except:
            logger.error("Cannot generate error message");
        return None