from django.db import models
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from django.db.models import permalink
from django.contrib.auth.models import User
from common import fields 
from common.crypto import BCipher
from django.conf import settings

class ProjectManager(models.Manager):
    
    def by_authorized(self, user):
        if user is not None and user.is_authenticated():
            return self.filter(
                               Q(enabled=True) | Q(maintainers__id__exact=user.id)
                               ).distinct() 
        else:
            return self.filter(enabled=True)
    
class Project(models.Model):
    """ 
    A project is a collection of resources
    >>> from auditor import middleware
    >>> from django.contrib.auth.models import User
    >>> u = User.objects.create(username="test",password="Test")
    >>> u = User.objects.get(username="test")
    >>> middleware.LOGGED_USER = u
    >>> p = Project.objects.create(name="Foo Test")
    >>> p = Project.objects.get(slug="foo-test")
    >>> p
    <Project: Foo Test>
    >>> p.delete()
    """
    
    slug = fields.AutoSlugField(max_length=50, unique=True, editable=False,
                    prepopulate_from="name", force_update=False)
    name = models.CharField(unique=True, verbose_name=_('Name'), max_length=50,
                            help_text=_('The project name to show to the users'))
    description = models.CharField(verbose_name=_('Description'),max_length=200, blank=True, help_text=_("A short Description"))
    hidden = models.BooleanField(default=False,
        help_text=_('Check to hide this project from the list view'))    
    enabled = models.BooleanField(verbose_name=_('Enabled'), default=True,
        help_text=_('Uncheck to disable this project'), db_index=True)
    read_only = models.BooleanField(verbose_name=_('Read only'), default=False,
        help_text=_('Check to disable modifications (to all dependent components)'))
    created = models.DateTimeField(auto_now_add=True, editable=False)
    modified = models.DateTimeField(auto_now=True, editable=False)
    vcsurl = models.CharField(verbose_name=_('Repository URL'), max_length=200, blank=False, help_text=_("Subversion repository URL"))
    viewurl = models.URLField(verbose_name=_('View Repository URL'), blank=True, verify_exists=False, null=True)
    viewurlparams = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('View URL parameters'), help_text=_("Parameters separated by semicolon (;). Ex: view=log;down=False"))
    
    repo_type = models.CharField(choices=settings.REPOSITORIES,
                                 verbose_name=_('Repository Type'),
                                 max_length=20)
    repo_user = models.CharField(max_length=50,
                                 verbose_name=_('Username'),
                                 blank=True,
                                 null=True,
                                 help_text=_("Some repositories requires authentication for checkout."))
    repo_pwd = models.CharField(max_length=100,
                                 verbose_name=_('Password'),
                                 blank=True,
                                 null=True)
    maintainers = models.ManyToManyField(User, related_name='projects_maintaining',
                                         blank=True, null=True, verbose_name=_("Project maintainers"))
    
    objects = ProjectManager()
    
    def __unicode__(self):
        return _(u'Project: %s') % self.name

    def __repr__(self):
        return '<Project: %s>' % self.name
    
    def set_repo_pwd(self, clear_text):
        bc = BCipher()
        setattr(self, 'repo_pwd', bc.encrypt(clear_text))

    def get_repo_pwd(self):
        value = getattr(self, 'repo_pwd')
        if value is not None:
            bc = BCipher()
            return bc.decrypt(value)
        return value
    
    class Meta:
        db_table  = 'projects'
        ordering  = ('name',)
        get_latest_by = 'created'
    
    def is_maintainer(self, user):
        if (user.is_superuser or 
                (user in self.maintainers.all())):
            return True
        return False
            
    @permalink
    def get_absolute_url(self):
        return ('project_detail', None, { 'slug': self.slug })
