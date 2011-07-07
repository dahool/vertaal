from os import environ
environ['DJANGO_SETTINGS_MODULE'] = 'settings'

#from settings import *
from django.conf import settings

from glob import glob
import os.path
from vertaalevolve.models import AppVersion
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

PATH = os.path.normpath(os.path.abspath(os.path.dirname(__file__)))

print "Executing update"

for ver in settings.VERSION_HIST:
    filename = os.path.join(PATH,'vertaalevolve','updates','ver_' + ver.replace('.','_') + ".py")
    try:
        av = AppVersion.objects.get(version=ver)
    except AppVersion.DoesNotExist:
        if os.path.exists(filename):
            print "Apply version patch %s" % ver
            try:
                execfile(filename)
            except IOError, e:
                print e          
            else:
                AppVersion.objects.create(version=ver)
        else:
            print "No updates available for %s" % ver
            AppVersion.objects.create(version=ver)
    else:
        print "Version %s is ok" % ver
        
# CURRENT
ver = settings.VERSION
filename = os.path.join(PATH,'vertaalevolve','updates','ver_' + ver.replace('.','_') + ".py")
try:
    av = AppVersion.objects.get(version=ver)
except AppVersion.DoesNotExist:
    if os.path.exists(filename):
        print "Apply version patch %s" % ver
        try:
            execfile(filename)
        except IOError, e:
            print e          
        else:
            AppVersion.objects.create(version=ver)
    else:
        print "No updates available for %s" % ver
        AppVersion.objects.create(version=ver)
else:
    print "Version %s is ok" % ver

print "Done"        