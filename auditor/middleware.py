#from django.conf import settings
import random
import datetime

LOGGED_USER = None
REQUEST_SESSION_ID = None
 
class AuditMiddleware(object):
    def __init__(self):
        global LOGGED_USER
        global REQUEST_SESSION_ID
        LOGGED_USER = None
        
    def process_request(self, request):
        global LOGGED_USER
        global REQUEST_SESSION_ID
        LOGGED_USER = request.user
        #REQUEST_SESSION_ID = request.COOKIES[settings.SESSION_COOKIE_NAME]
        REQUEST_SESSION_ID = "%d-%s-%d" % (random.randint(100,999),
                                           datetime.datetime.utcnow().strftime('%d%m%H%M%S'),
                                           random.randint(10,99))
        return None