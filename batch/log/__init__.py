import logging
import logging.handlers

from django.db.models import get_app
from django.db.models.signals import *
from django.conf import settings

DEFAULT_LOG_LEVEL = logging.INFO
log_level = getattr(settings, 'BATCH_LOG_LEVEL', DEFAULT_LOG_LEVEL)

_logger = logging.getLogger('batch-vertaal')
_handler = logging.handlers.RotatingFileHandler(
              getattr(settings, 'BATCH_LOG_FILENAME'), maxBytes=5242880, backupCount=10)
_formatter = logging.Formatter(
    '[%(asctime)s %(filename)s %(levelname)s %(module)s (%(lineno)d)] %(funcName)s: %(message)s')
_handler.setFormatter(_formatter)
_logger.addHandler(_handler)
_logger.setLevel(log_level)

logger = _logger 