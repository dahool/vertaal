import os
import logging
import logging.handlers
from django.conf import settings

RPC_LOG_FILENAME = getattr(settings, 'RPC_LOG_FILENAME')

if not os.path.exists(os.path.dirname(RPC_LOG_FILENAME)):
    os.makedirs(os.path.dirname(RPC_LOG_FILENAME))
    
DEFAULT_LOG_LEVEL = logging.INFO
log_level = getattr(settings, 'RPC_LOG_LEVEL', DEFAULT_LOG_LEVEL)

_logger = logging.getLogger('rpc-vertaal')
_handler = logging.handlers.RotatingFileHandler(
              RPC_LOG_FILENAME, maxBytes=5242880, backupCount=10)
_formatter = logging.Formatter(
    '[%(asctime)s %(filename)s %(levelname)s %(module)s (%(lineno)d)] %(funcName)s: %(message)s')
_handler.setFormatter(_formatter)
_logger.addHandler(_handler)
_logger.setLevel(log_level)

logger = _logger 