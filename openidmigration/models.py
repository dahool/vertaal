# -*- coding: utf-8 -*-
"""Copyright (c) 2014 Sergio Gabriel Teves
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
from django.contrib.auth.models import User
import datetime
from django.conf import settings

class MigrationTokenManager(models.Manager):
    use_for_related_fields = True
    
    def valid(self):
        meta_diff = datetime.datetime.now() - datetime.timedelta(days=getattr(settings, 'MIG_EXPIRES', 2))
        return self.filter(used=False, created__gte=meta_diff)
    
class MigrationToken(models.Model):
    
    token = models.CharField(max_length=40, primary_key=True)
    created = models.DateTimeField(auto_now_add=True)
    used = models.BooleanField(default=False)
    user = models.ForeignKey(User, related_name="migtoken")
    
    objects = MigrationTokenManager()
    
    def __unicode__(self):
        return self.token

    def __repr__(self):
        return self.user
    
    class Meta:
        db_table  = 'migtokens'