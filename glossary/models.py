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
import re

from django.db import models
from django.db.models import permalink
from django.utils.translation import ugettext_lazy as _
from languages.models import Language
from projects.models import Project
from django.contrib.auth.models import User

initial_pat = '([ ]([a-zA-Z]))|(^([a-zA-Z]))'

ACTIONS = {'ADDITION': 'A',
           'CHANGE': 'C'}

ACTION_CHOICES = (
    ('A', _('Addition')),
    ('C', _('Change'))
)

class Glossary(models.Model):
    '''Glossary
    '''
    word = models.CharField(max_length=255,
                            help_text=_('Original word'),
                            verbose_name=_('Word'), db_index=True)
    translation = models.CharField(max_length=255,
                                   help_text=_('Recommended translations'))
    comment = models.CharField(max_length=500,
                           help_text=_('Comments'),
                           blank=True, default='')
    added = models.DateTimeField(auto_now_add=True)
    language = models.ForeignKey(Language)
    project = models.ForeignKey(Project)
    initial = models.CharField(max_length=1, blank=True, default='', db_index=True)
    
    def __unicode__(self):
        return u"%(word)s - %(lang)s" % {
            'word': self.word,
            'lang': self.language}

    def __repr__(self):
        return '<Glossary: %s [%s]>' % (self.word, self.language.code)
    
    class Meta:
        unique_together = ("word","project","language")
        db_table  = 'glossary'
        ordering  = ('initial','word',)        

    @permalink
    def get_absolute_url(self):
        return ('gloss_detail', None, { 'word': self.word, 'lang': self.language.code })

    def save(self, *args, **kwargs):
        self.__find_initial()
        super(Glossary, self).save(*args, **kwargs)
        
    def __find_initial(self):
        try:
            m = re.search(initial_pat, self.word)
            if m is not None:
                if m.group(2) is None:
                    self.initial = m.group(4).lower()
                else:
                    self.initial = m.group(2).lower()
            else:
                self.initial = self.word[0:1].lower()        
        except:
            self.initial = self.word[0:1].lower()
            
class GlossaryLog(models.Model):
    user = models.ForeignKey(User)
    glossary = models.ForeignKey(Glossary, related_name='history')
    created = models.DateTimeField(auto_now_add=True)
    translation = models.CharField(max_length=255)
    action_flag = models.CharField(max_length=1, choices=ACTION_CHOICES, db_index=True)
    
    class Meta:
        db_table = 'glossary_logs'
        get_latest_by = 'created'
        ordering = ('-created',)