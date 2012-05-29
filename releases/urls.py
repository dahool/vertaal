from django.conf.urls.defaults import patterns, url, include
from django.contrib import admin
from releases.models import *
from releases.views import *

admin.autodiscover()

urlpatterns = patterns('',
    url(
        regex = '^(?P<project>[-\w]+)/add/$',
        view = release_create_update,
        name = 'release_create'),
    url(
        regex = '^(?P<slug>[-\w]+)/edit/$',
        view = release_create_update,
        name = 'release_edit',),
    url(
        regex = '^(?P<slug>[-\w]+)/delete/$',
        view = release_delete,
        name = 'release_delete',),
    url(
        regex = '^(?P<slug>[-\w]+)/populate/$',
        view = release_populate,
        name = 'release_populate',),
    url(
        regex = '^(?P<slug>[-\w]+)/merge/$',
        view = multimerge,
        name = 'multimerge',),
    url(
        regex = '^(?P<slug>[-\w]+)/$',
        view = release_detail,
        name = 'release_detail',),
    url(
        regex = '^(?P<project>[-\w]+)/(?P<release>[-\w]+)/log/$',
        view = build_log,
        name = 'build_log',),        
) 