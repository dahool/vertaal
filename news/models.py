from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.db.models import permalink
from common import fields

class Article(models.Model):
    
    slug = fields.AutoSlugField(max_length=80, unique=True, editable=False,
                    prepopulate_from="title", force_update=False) 
    title = models.CharField(max_length=80, verbose_name=_('Title'))
    hometext = models.TextField(verbose_name=_('Brief'))
    bodytext = models.TextField(verbose_name=_('Body'), blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    updated = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(User)
    
    def __unicode__(self):
        return self.title

    def __repr__(self):
        return self.slug
    
    @permalink
    def get_absolute_url(self):
        return ('news_view', None, { 'slug': self.slug })
    
    class Meta:
        db_table  = 'news'
        ordering  = ('-created',)
        get_latest_by = 'created'