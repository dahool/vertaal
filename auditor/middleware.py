import random
import datetime
 
class AuditMiddleware(object):
        
    def process_request(self, request):
        from auditor import AUDIT_SESSION_ID
        auditSessionId = "%d-%s-%d" % (random.randint(100,999),
                                           datetime.datetime.utcnow().strftime('%d%m%H%M%S'),
                                           random.randint(10,99))
        setattr(request, AUDIT_SESSION_ID, auditSessionId)
        return None