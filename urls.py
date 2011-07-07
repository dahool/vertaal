from django.conf.urls.defaults import *
from django.conf import settings
from django.contrib import admin

admin.autodiscover()

#handler404 = 'middleware.views.not_found'

urlpatterns = patterns('',
    url(r'^$', 'app.views.index', name='home'),
    url(r'^v2guser/$', 'app.views.v2gwelcome'),
    url(r'^app/', include('app.urls')),
    url(r'^accounts/', include('registration.urls')),
    url(r'^projects/', include('projects.urls')),
    url(r'^releases/', include('releases.urls')),
    url(r'^languages/', include('languages.urls')),
    url(r'^contact/', include('contact.urls')),
    url(r'^profile/', include('userprofileapp.urls')),
    url(r'^components/', include('components.urls')),
    url(r'^teams/', include('teams.urls')),
    url(r'^files/', include('files.urls')),
    url(r'^iterm/', include('glossary.urls')),
    url(r'^news/', include('news.urls')),
    url(r'^man/(.*)', admin.site.root),
) 

def disabled(request):
    from django.http import HttpResponseGone
    return HttpResponseGone()

if settings.ENABLE_RSS:
    urlpatterns += patterns('',    
        url(r'^feeds/', include('appfeeds.urls')),
    )
else:    
    urlpatterns += patterns('',    
        url(r'^feeds/', disabled),
    )

if settings.ENABLE_OPENID:
    urlpatterns += patterns('',    
        url(r'^openid/', include('django_authopenid.urls')),
    )

if settings.ENABLE_RPC:
    urlpatterns += patterns('',
        url(r'xmlrpc/$', 'django_xmlrpc.views.handle_xmlrpc',),
    )
    
if settings.STATIC_SERVE:
    urlpatterns += patterns('',
        (r'^site_media/(?P<path>.*)$', 'django.views.static.serve',
         {'document_root': settings.MEDIA_ROOT}),
    )