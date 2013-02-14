# -*- coding: utf-8 -*-
"""Copyright (c) 2012, Sergio Gabriel Teves
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
from logging import Formatter, Filter
from logging.handlers import RotatingFileHandler

class UserFormatter(Formatter):

    formatter = None
    
    def __init__(self, fmt=None, datefmt=None):
        self.formatter = Formatter(fmt, datefmt)
            
    def format(self, record):
        from auditor import AUDIT_SESSION_ID
        from common.middleware import threadlocal        
        
        user = threadlocal.get_current_user()
        if user and user.is_authenticated():
            username = user.username
        else:
            username = 'Anonymous'
        request = threadlocal.get_current_request()
        if request and getattr(request, AUDIT_SESSION_ID):
            sessionid = getattr(request, AUDIT_SESSION_ID)
        else:
            sessionid = "None"
        setattr(record, 'username', username)
        setattr(record, 'sessionid', sessionid)
        return self.formatter.format(record)

class UserFilter(Filter):

    def filter(self, record):
        from auditor import AUDIT_SESSION_ID
        from common.middleware import threadlocal
        
        user = threadlocal.get_current_user()
        if user and user.is_authenticated():
            username = user.username
        else:
            username = 'Anonymous'
        request = threadlocal.get_current_request()
        if request and getattr(request, AUDIT_SESSION_ID):
            sessionid = getattr(request, AUDIT_SESSION_ID)
        else:
            sessionid = "None"
        setattr(record, 'username', username)
        setattr(record, 'sessionid', sessionid)
        return True
    
class ChmodRotatingFileHandler(RotatingFileHandler):
    
    def __init__(self, filename, **kw):
        self.filename = filename
        RotatingFileHandler.__init__(self, filename, **kw)
    
    def doRollover(self):
        import os
        RotatingFileHandler.doRollover(self)
        os.chmod(self.filename, int('755',8))