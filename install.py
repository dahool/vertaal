from os import environ
environ['DJANGO_SETTINGS_MODULE'] = 'settings'

from django.conf import settings

from django.contrib.sites.models import Site

try:
    current_site = Site.objects.get_current()
    if current_site.domain <> settings.SITE_DOMAIN:
        current_site.domain = settings.SITE_DOMAIN
        current_site.name = settings.PROJECT_NAME
        current_site.save()
        Site.objects.clear_cache()
except:
    pass

# -- SETUP INITIAL GROUPS -- #
from django.contrib.auth.models import User, Group, Permission
g = Group.objects.create(name='Coordinator')
g.permissions.add(
                  Permission.objects.get(codename='add_glossary'),
                  Permission.objects.get(codename='change_glossary')
                  )

u = User(username=getattr(settings, 'BOT_USERNAME','bot'))
u.set_unusable_password()
u.is_active = False
u.save()