from django.conf.urls.defaults import patterns, url, include
from django.contrib import admin
from app.views import *

urlpatterns = patterns('',
    url(r'^log/(?P<file>[-\w_]+)/$', get_log, name='get_log'),
) 
