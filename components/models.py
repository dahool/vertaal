from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.db.models import permalink
from projects.models import Project
from common import fields 

class Component(models.Model):
    """ 
    A component is a sub project under a release
    >>> from auditor import middleware
    >>> from django.contrib.auth.models import User
    >>> from projects.models import Project
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
    >>> c = Component.objects.create(name="Bar Foo", release=b)
    >>> c = Component.objects.get(slug="bar-foo")
    >>> c
    <Component: Bar Foo - Project: Foo Test>
    >>> c.delete()
    >>> b.delete()
    >>> p.delete()
    """

    slug = fields.AutoSlugField(max_length=50, unique=True,
                            help_text=_('A short label to be used in the URL, containing only '
                    'letters, numbers, underscores or hyphens.'), editable=False,
                    prepopulate_from="name", force_update=False)
    name = models.CharField(max_length=50,verbose_name=_('Name'),
                            help_text=_('The name to show to the users'))
    created = models.DateTimeField(auto_now_add=True, editable=False)
    modified = models.DateTimeField(auto_now=True, editable=False)
    vcspath = models.CharField(verbose_name=_('Repository Path'), max_length=200, help_text=_("Name of the parent folder."))
    format = models.CharField(verbose_name=_('Location format'), max_length=200,
                            help_text=_('Default format is $PATH/$LANG/po.'),
                                      default='$PATH/$LANG/po')
    project = models.ForeignKey(Project, related_name="components")
    potlocation = models.CharField(max_length=50,verbose_name=_('POT Path'),
                                   blank=True, null=True)
    
    def __unicode__(self):
        return _('Component: %(component)s - Project: %(project)s') % {'component': self.name, 'project': self.project.name}

    def __repr__(self):
        return '<Component: %s - Project: %s>' % (self.name, self.project.name)
    
    def get_path(self, language_code):
        return self.format.replace('$PATH',self.vcspath).replace('$LANG',language_code)
        
    @permalink
    def get_absolute_url(self):
        return ('component_detail', None, { 'slug': self.slug })
    
    class Meta:
        db_table  = 'components'
        unique_together = ("project","name")
        ordering  = ('name',)
        get_latest_by = 'created'