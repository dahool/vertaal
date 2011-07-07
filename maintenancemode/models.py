from django.utils.translation import ugettext as _
from django.db import models
from django.contrib.sites.models import Site

class SiteStatus(models.Model):
    site = models.ForeignKey(Site, unique=True, related_name='site_status')
    enabled = models.BooleanField(default=True)

    def __unicode__(self):
        if self.enabled:
            return _('Enabled')
        else:
            return _('Disabled')

    def __repr__(self):
        return self.__unicode__()
    
    class Meta:
        db_table  = 'site_status'