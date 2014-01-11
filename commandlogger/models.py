"""Copyright (c) 20012 Sergio Gabriel Teves
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

class CommandLog(models.Model):
    command = models.CharField(max_length=100,verbose_name=_('Name'), primary_key=True)
    lastrun = models.DateTimeField(auto_now_add=True, auto_now=True, editable=False)
    exception = models.CharField(verbose_name=_('Exception'), max_length=500, null=True)
    response = models.CharField(verbose_name=_('Response'), max_length=500, null=True)
    success = models.BooleanField(default=True)
    duration = models.IntegerField(default=0)
    
    def __unicode__(self):
        return _('%(command)s - Success: %(success)s - %(run)s - %(response)s') % {'command': self.command, 'success': self.success, 'run': self.lastrun, 'response': self.response}

    def __repr__(self):
        return '<%(command)s - %(success)s - %(run)s>' % {'command': self.command, 'success': self.success, 'run': self.lastrun}
    
    class Meta:
        ordering  = ('-lastrun', 'command')
        get_latest_by = 'lastrun'