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
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.db.models import permalink
import datetime
from common import fields

from django.core.validators import MaxLengthValidator
from django.utils.html import strip_tags

class MaxLengthStripHtmlValidator(MaxLengthValidator):
    clean   = lambda self, x: len(strip_tags(x))    

class ArticleManager(models.Manager):

    def all_active(self):
        return self.all().exclude(expires__lt=datetime.date.today())
        
class Article(models.Model):
    
    slug = fields.AutoSlugField(max_length=80, unique=True, editable=False,
                    prepopulate_from="title", force_update=False) 
    title = models.CharField(max_length=80, verbose_name=_('Title'))
    hometext = models.TextField(verbose_name=_('Brief'), validators=[MaxLengthStripHtmlValidator(150)])
    bodytext = models.TextField(verbose_name=_('Body'), blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name=_('Created'))
    updated = models.DateTimeField(auto_now=True)
    expires = models.DateField(verbose_name=_('Expires'), blank=True, null=True, db_index=True)
    author = models.ForeignKey(User, verbose_name=_('Author'))
    
    objects = ArticleManager()
    
    def __unicode__(self):
        return self.title

    def __repr__(self):
        return self.slug
    
    @permalink
    def get_absolute_url(self):
        return ('news_view', None, { 'slug': self.slug })
    
    class Meta:
        db_table  = 'news'
        ordering  = ('expires', '-created',)
        get_latest_by = 'created'