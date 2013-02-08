from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('releases.views',
    url(r'^(?P<project>[-\w]+)/add/$', 'release_create_update', name = 'release_create'),
    url(r'^(?P<slug>[-\w]+)/edit/$', 'release_create_update', name = 'release_edit',),
    url(r'^(?P<slug>[-\w]+)/delete/$', 'release_delete', name = 'release_delete',),
    url(r'^(?P<slug>[-\w]+)/populate/$', 'release_populate', name = 'release_populate',),
    url(r'^(?P<slug>[-\w]+)/merge/$', 'multimerge', name = 'multimerge',),
    url(r'^(?P<slug>[-\w]+)/$', 'release_detail', name = 'release_detail',),
    url(r'^(?P<project>[-\w]+)/(?P<release>[-\w]+)/log/$', 'build_log', name = 'build_log',),        
)