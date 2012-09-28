# -*- coding: utf-8 -*-
from django.db import models
from django.utils.encoding import smart_unicode
from files.models import POFileSubmit
from django.contrib.auth.models import User

class POFileSubmitDeferredManager(models.Manager):
    
    def get_ordered(self):
        return self.filter(locked=False, filesubmit__locked=True).order_by('filesubmit__pofile__release__project', 'user')
            
class POFileSubmitDeferred(models.Model):
    filesubmit = models.ForeignKey(POFileSubmit, related_name='deferred')
    user = models.ForeignKey(User)
    created = models.DateTimeField(auto_now=True, auto_now_add=True)
    repo_user = models.CharField(max_length=50, blank=True, null=True, editable=False)
    repo_pwd = models.CharField(max_length=100, blank=True, null=True, editable=False)
    message = models.CharField(max_length=255, blank=True, null=True)
    locked = models.BooleanField(default=False, db_index=True)
    objects = POFileSubmitDeferredManager()
    
    def __unicode__(self):
        return u"%s [%s]" % (self.filesubmit, self.created)

    def __repr__(self):
        return '<%(file)s (%(created)s)>' % {'file': self.filesubmit, 'created': self.created}
        
    def lock(self, value = True):
        self.locked = value
        self.save()
        
    class Meta:
        db_table  = 'submitqueue'
        get_latest_by = 'created'
