import logging
import logging.handlers
import traceback
from django.conf import settings
from exceptionlogger.models import *

_logger = logging.getLogger('error-vertaal')
_handler = logging.handlers.RotatingFileHandler(
              getattr(settings, 'ERROR_LOG_FILENAME'), maxBytes=5242880, backupCount=10)
_formatter = logging.Formatter(
    '[%(asctime)s: %(message)s')
_handler.setFormatter(_formatter)
_logger.addHandler(_handler)
_logger.setLevel(logging.ERROR)

logger = _logger 

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
        

