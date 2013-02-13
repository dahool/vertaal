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