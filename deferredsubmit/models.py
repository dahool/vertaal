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
