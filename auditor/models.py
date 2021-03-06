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
from django.utils.encoding import smart_unicode

ACTIONS = {'ADDITION': 'A',
           'CHANGE': 'C',
           'DELETION': 'D'}

ACTION_CHOICES = (
    ('A', _('Addition')),
    ('C', _('Change')),
    ('D', _('Deletion')),
)

class Audit(models.Model):
    """
    >>> u = User.objects.create(username="test",password="test")
    >>> a = Audit.objects.create(user=u, object_repr='REP', action_flag='A')
    >>> a = Audit.objects.get(id=1)
    >>> a.object_repr
    u'REP'
    >>> len(u.tx_actions.all())
    1
    >>> u.tx_actions.all()[0] == a
    True
    """
    created = models.DateTimeField(auto_now_add=True, editable=False)
    user = models.ForeignKey(User, related_name="tx_actions")
    object_type = models.CharField(max_length=255, default='')
    object_id = models.TextField(blank=True, null=True) 
    object_repr = models.CharField(max_length=255)
    action_flag = models.CharField(max_length=1, choices=ACTION_CHOICES, db_index=True)

    def __unicode__(self):
        return u"%s - [%s] %s by %s" % (smart_unicode(self.created),
                                 self.get_action_flag_display(),
                                 self.object_repr,
                                 self.user)

    def __repr__(self):
        return self.object_repr 
    
    def save(self, *args, **kwargs):
        self.object_repr = self.object_repr[:255]
        super(Audit, self).save(*args, **kwargs)        

    class Meta:
        db_table  = 'audit'
        ordering  = ('-created',)