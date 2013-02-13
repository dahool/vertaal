from django.contrib.sites.models import Site
from django.conf import settings
from auditor import audit_model

try:
    if getattr(settings, 'AUDIT_MODEL',True):
        audit_model('projects.Project')
        audit_model('releases.Release')
        audit_model('components.Component')
        audit_model('teams.Team')
        audit_model('glossary.Glossary')
except:
    pass
