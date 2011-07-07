import os
import stat
import logging
import logging.handlers

from django.db.models import get_app
from django.db.models.signals import *
from django.conf import settings
from auditor import middleware

class UserFormatter(logging.Formatter):

    formatter = None
    
    def __init__(self, fmt=None, datefmt=None):
        self.formatter = logging.Formatter(fmt, datefmt)
            
    def format(self, record):
        if middleware.LOGGED_USER and middleware.LOGGED_USER.is_authenticated():
            username = middleware.LOGGED_USER.username
        else:
            username = 'Anonymous'
        if middleware.REQUEST_SESSION_ID:
            sessionid = middleware.REQUEST_SESSION_ID
        else:
            sessionid = "None"
        setattr(record, 'username', username)
        setattr(record, 'sessionid', sessionid)
        return self.formatter.format(record)

class ChmodRotatingFileHandler(logging.handlers.RotatingFileHandler):
    
    def doRollover(self):
        logging.handlers.RotatingFileHandler.doRollover(self)
        os.chmod(LOG_FILENAME, int('666',8))    
    
LOG_FILENAME = getattr(settings, 'LOG_FILENAME')

if not os.path.exists(os.path.dirname(LOG_FILENAME)):
    os.makedirs(os.path.dirname(LOG_FILENAME))
    os.chmod(LOG_FILENAME, int('666',8))
    
DEFAULT_LOG_LEVEL = logging.INFO
log_level = getattr(settings, 'LOG_LEVEL', DEFAULT_LOG_LEVEL)

_logger = logging.getLogger('vertaal')
_handler = ChmodRotatingFileHandler(
              LOG_FILENAME, maxBytes=5242880, backupCount=10)
_formatter = UserFormatter(
    '[%(asctime)s %(filename)s %(levelname)s %(module)s (%(lineno)d)] <%(username)s> [%(sessionid)s] %(funcName)s: %(message)s')
_handler.setFormatter(_formatter)
_logger.addHandler(_handler)
_logger.setLevel(log_level)

logger = _logger 