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
from django.conf import settings
from components.models import *
from releases.models import *
from datetime import datetime, timedelta

class BuildCacheManager(models.Manager):
    
    def get_locked(self, release):
        q = self.filter(release=release,locked=True,lock_expires__gt=datetime.now())
        return q
    
    def by_language(self, language):
        """ Returns a list of objects statistics for a language."""
        q = self.filter(language=language)
        q.order_by('language')
        return q


class BuildCache(models.Model):
    component = models.ForeignKey(Component)
    release = models.ForeignKey(Release)
    updated = models.DateTimeField(auto_now_add=True, auto_now=True)
    rev = models.CharField(max_length=10, null=True, blank=True)
    locked = models.BooleanField(default=False)
    lock_expires = models.DateTimeField(null=True, blank=True)
    
    objects = BuildCacheManager()
    
    def __unicode__(self):
        return repr(self)
    
    def __repr__(self):
        return u"%s - %s" % (self.release.name,self.component.name)
    
    @property
    def is_expired(self):
        if self.lock_expires is None:
            return True
        return not (datetime.now() < self.lock_expires)

    @property
    def is_locked(self):
        if self.locked and not self.is_expired: 
            return True
        return False
    
    def lock(self, save=True):
        self.locked = True
        self.lock_expires = datetime.now() + timedelta(minutes=getattr(settings, 'AUTO_UNLOCK_BUILD', 30))
        if save:
            self.save()
            
    def unlock(self, save=True):
        self.locked = False
        self.lock_expires = None
        if save:
            self.save()
            
    def setrev(self, rev):
        try:
            if self.rev is None:
                self.rev = rev
            elif rev is not None:
                if long(self.rev) < long(rev):
                    self.rev = rev
        except:
            self.rev = rev
             
    class Meta:
        unique_together = ("release","component")
        db_table = 'build_cache'
        