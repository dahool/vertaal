from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.db.models import permalink
#from django.db.models import Q
import datetime
from common import fields

class ArticleManager(models.Manager):

    def all_active(self):
        #return self.filter(Q(expires=None) | Q(expires__lte=datetime.date.today()))
        return self.all().exclude(expires__lt=datetime.date.today())
        
class Article(models.Model):
    
    slug = fields.AutoSlugField(max_length=80, unique=True, editable=False,
                    prepopulate_from="title", force_update=False) 
    title = models.CharField(max_length=80, verbose_name=_('Title'))
    hometext = models.TextField(verbose_name=_('Brief'))
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