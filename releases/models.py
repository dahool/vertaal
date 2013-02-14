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
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from projects.models import Project
from django.db.models import permalink
from common import fields 

from common.middleware import threadlocal

class ReleaseManager(models.Manager):
    use_for_related_fields = True

    def all(self):
        user = threadlocal.get_current_user()
        q = self.get_query_set()
        if user:
            q.query.add_q((Q(enabled=True) & Q(project__enabled=True)) | Q(project__maintainers__id__exact=user.id))
            q.query.distinct = True
        else:
            q.query.add_q(Q(enabled=True) & Q(project__enabled=True))
        return q
    
    def by_authorized(self, user):
        if user.is_authenticated():
            return self.filter(
                               (Q(enabled=True) & Q(project__enabled=True))
                                | Q(project__maintainers__id__exact=user.id)
                               ).distinct('id') 
        else:
            return self.filter(enabled=True, project__enabled=True)        
        
class Release(models.Model):
    """ 
    A Release is a set of sub projects under a main project
    >>> from auditor import middleware
    >>> from django.contrib.auth.models import User
    >>> u = User.objects.create(username="test",password="Test")
    >>> u = User.objects.get(username="test")
    >>> middleware.LOGGED_USER = u    
    >>> p = Project.objects.create(name="Foo Test")
    >>> p = Project.objects.get(slug="foo-test")
    >>> p
    <Project: Foo Test>
    >>> b = Release.objects.create(name="Foo Bar", project=p)
    >>> b = Release.objects.get(slug="foo-bar")
    >>> b
    <Release: Foo Bar - Project: Foo Test>
    >>> b.delete()
    >>> p.delete()
    """
    
    slug = fields.AutoSlugField(max_length=50, unique=True,
                            help_text=_('A short label to be used in the URL, containing only '
                    'letters, numbers, underscores or hyphens.'), editable=False,
                    prepopulate_from="name", force_update=False)
    name = models.CharField(max_length=50,verbose_name=_('Name'),
                            help_text=_('The name to show to the users'))
    hidden = models.BooleanField(default=False,
        help_text=_('Hide this object from the list view?'))    
    enabled = models.BooleanField(default=True,verbose_name=_('Enabled'),
        help_text=_('Uncheck to disable this release'), db_index=True)
    read_only = models.BooleanField(default=False,verbose_name=_('Read only'),
        help_text=_('Check to disable modifications (to all dependent components)'))
    created = models.DateTimeField(auto_now_add=True, editable=False)
    modified = models.DateTimeField(auto_now=True, editable=False)
    vcsbranch = models.CharField(verbose_name=_('Repository Path'), max_length=200, help_text=_("The repository path, usually trunk or branch name"))
    project = models.ForeignKey(Project, related_name="releases")

    objects = ReleaseManager()
    
    def __unicode__(self):
        return _(u'Release: %(release)s - Project: %(project)s') % {'release': self.name, 'project': self.project.name}

    def __repr__(self):
        return '<Release: %s - Project: %s>' % (self.name, self.project.name)
    
    class Meta:
        db_table  = 'releases'
        unique_together = ("project","name")
        ordering  = ('name',)
        get_latest_by = 'created'
        
    @permalink
    def get_absolute_url(self):
        return ('release_detail', None, { 'slug': self.slug })
 