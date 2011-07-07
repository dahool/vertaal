from django.db import models
from django.contrib.auth.models import User

class RpcSession(models.Model):
    user = models.ForeignKey(User)
    token = models.CharField(max_length=50, unique=True)
    created = models.DateTimeField(auto_now_add=True, auto_now=True)
    
    def __unicode__(self):
        return repr(self)

    def __repr__(self):
        return u'<Session: %s>' % self.user
    
    class Meta:
        db_table  = 'rpc_session'
        get_latest_by = 'created'    