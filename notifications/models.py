from django.db import models
from django.db.models import permalink
from django.contrib.auth.models import Message
from django.db.models.signals import post_save
from django.utils.encoding import smart_unicode

class UserMessages(models.Model):
    
    message = models.ForeignKey(Message, related_name="status")
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    notified = models.DateTimeField(null=True, blank=True)
    
    def __unicode__(self):
        return smart_unicode(self.message)

    class Meta:
        db_table  = 'user_messages_status'
        ordering  = ('created',)
        get_latest_by = 'created'
        verbose_name_plural = "User Messages"
        
def message_add_callback(sender, **kwargs):
    obj = kwargs['instance']
    if kwargs['created'] is True:
        try:
            obj.status.create()
        except:
            pass
    
post_save.connect(message_add_callback, sender=Message)