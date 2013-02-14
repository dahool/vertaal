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