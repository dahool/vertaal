#import os
#import stat
#import logging
#import logging.handlers
#
#from django.conf import settings
#
#from app.log.formatter import ChmodRotatingFileHandler, UserFormatter
#
#LOG_FILENAME = getattr(settings, 'LOG_FILENAME')
#
#if not os.path.exists(os.path.dirname(LOG_FILENAME)):
#    os.makedirs(os.path.dirname(LOG_FILENAME))
#    os.chmod(os.path.dirname(LOG_FILENAME), int('755',8))
#    
#DEFAULT_LOG_LEVEL = logging.INFO
#log_level = getattr(settings, 'LOG_LEVEL', DEFAULT_LOG_LEVEL)
#
#_logger = logging.getLogger('vertaal')
#_handler = ChmodRotatingFileHandler(
#              LOG_FILENAME, maxBytes=5242880, backupCount=10)
#_formatter = UserFormatter(
#    '[%(asctime)s %(filename)s %(levelname)s %(module)s (%(lineno)d)] <%(username)s> [%(sessionid)s] %(funcName)s: %(message)s')
#_handler.setFormatter(_formatter)
#_logger.addHandler(_handler)
#_logger.setLevel(log_level)
#
#logger = _logger 
