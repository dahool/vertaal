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