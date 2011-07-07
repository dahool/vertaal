from django.contrib.sites.models import Site
from django.conf import settings
from auditor import audit_model
import app.log

#try:
#    current_site = Site.objects.get_current()
#    if current_site.domain <> settings.SITE_DOMAIN:
#        current_site.domain = settings.SITE_DOMAIN
#        current_site.name = settings.PROJECT_NAME
#        current_site.save()
#        Site.objects.clear_cache()
#except:
#    pass

try:
    if getattr(settings, 'AUDIT_MODEL',True):
        audit_model(projects.models.Project)
        audit_model(releases.models.Release)
        audit_model(components.models.Component)
        audit_model(teams.models.Team)
        audit_model(glossary.models.Glossary)
except:
    pass
