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

class ExceptionLog(models.Model):
    
    date = models.DateTimeField(auto_now_add=True, db_index=True)
    exception = models.TextField(null=True, blank=True)
    stacktrace = models.TextField(null=True, blank=True)
    request = models.TextField(null=True, blank=True)
    
    def __unicode__(self):
        return '%s - %s' % (smart_unicode(self.date),smart_unicode(self.exception))
    
    def __repr__(self):
        return smart_unicode(self) 
    
    class Meta:
        ordering  = ('-date',)    