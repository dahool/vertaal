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
from dateutil.parser import *
import datetime
import re
import logging
logger = logging.getLogger('vertaal.files')

_CREATION_DATE = re.compile('.(POT-Creation-Date:)[ ](?P<date>[0-9]{4}[-][0-9]{2}[-][0-9]{2}[ ][0-9]{2}[:][0-9]{2}[+|-][0-9]{0,4})')

def extract_creation_date(filename):
    o = open(filename,'r')
    m = None
    for line in o.readlines():
        m = _CREATION_DATE.match(line)
        if m: break
        o.close()
    if m:
        dateval = m.group('date')
        try:
            dt = potdate_to_datetime(dateval)
            return dt
        except Exception, e:
            logger.error("Date conversion failed (%s)" % str(e))
    return None

def potdate_to_datetime(value):
    val = parse(value) # dateutil
    t = val.utctimetuple()
    return datetime.datetime(t.tm_year,t.tm_mon,t.tm_mday,t.tm_hour,t.tm_min)    
