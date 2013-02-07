# -*- coding: utf-8 -*-
"""Copyright (c) 2013, Sergio Gabriel Teves
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
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from app.auth import get_user_model
from djangopm.utils import send_pm

class MessageManager(models.Manager):
    use_for_related_fields = True
    
    def unread(self):
        return self.filter(unread=True)
    
    def read(self):
        return self.filter(unread=False)
     
    def draft(self):
        return self.filter(unread=True) 
    
class PMUser(User):
    
    def private_message(self, subject, message):
        send_pm(self, subject, message)
    
    class Meta:
        proxy=True
    
class PMMessage(models.Model):
    sender = models.ForeignKey(get_user_model(), null=True, blank=True)
    recipients = models.ManyToManyField(get_user_model(), null=True, blank=True, related_name="+", verbose_name=_('To'))
    created = models.DateTimeField(auto_now=True)
    draft = models.BooleanField(default=True)
    subject = models.CharField(max_length=100, verbose_name=_('Subject'))
    text = models.TextField(verbose_name=_('Message'))
    
    def __unicode__(self):
        return self.subject
        
    class Meta:
        ordering  = ('-created',)
        get_latest_by = 'created'
        
    @property
    def message(self):
        return self
    
    def get_absolute_url(self):
        return reverse('pm_detail', args=[str(self.id)])
        
class PMInbox(models.Model):
    user = models.ForeignKey(get_user_model(), related_name="pm_inbox")
    message = models.ForeignKey(PMMessage)
    unread = models.BooleanField(default=True)
    notified = models.DateTimeField(null=True, blank=True)

    objects = MessageManager()
    
    def __unicode__(self):
        return self.message.subject
        
    class Meta:
        ordering  = ('-message__created',)
        get_latest_by = 'message__created'
        
    def get_absolute_url(self):
        return reverse('pm_detail_in', args=[str(self.id)])

class PMOutbox(models.Model):
    user = models.ForeignKey(get_user_model(), related_name="pm_outbox")
    message = models.ForeignKey(PMMessage)
    
    def __unicode__(self):
        return self.message.subject
        
    class Meta:
        ordering  = ('-message__created',)
        get_latest_by = 'message__created'
        
    def get_absolute_url(self):
        return reverse('pm_detail_out', args=[str(self.id)])
    
from django.db.models.signals import post_save

def pmmessage_postsave_handler(instance, **kw):
    if not instance.draft:
        if instance.sender:
            PMOutbox.objects.create(user=instance.sender, message=instance)
        for u in instance.recipients.all():
            PMInbox.objects.create(user=u, message=instance)

post_save.connect(pmmessage_postsave_handler, sender=PMMessage, dispatch_uid="pmmessage_postsave_handler")
    