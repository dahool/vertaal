# -*- coding: utf-8 -*-
"""Copyright (c) 2008-2012 Sergio Gabriel Teves
All rights reserved.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
from django.conf.urls import *
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings
from django.contrib import admin

handler404 = 'common.middleware.views.not_found'
handler500 = 'common.middleware.views.server_error'
handler503 = 'common.middleware.views.unavailable'

js_info_dict = {
    'domain': 'djangojs',
    'packages': ('vertaal',),
}

admin.autodiscover()

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
    url(r'^grappelli/', include('grappelli.urls')), # grappelli URLS
    url(r'^man/', include(admin.site.urls)),
    url(r'^pm/', include('djangopm.urls')),
    url(r'^jsi18n/$', 'django.views.i18n.javascript_catalog', js_info_dict),
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

if settings.ENABLE_RPC:
    urlpatterns += patterns('',
        url(r'xmlrpc/$', 'django_xmlrpc.views.handle_xmlrpc',),
    )

if getattr(settings, 'ENABLE_MIG', False):
    urlpatterns = patterns('',
        url(r'^', include('openidmigration.urls'),),
        url(r'^accounts/', include('registration.urls')),
        url(r'^man/', include(admin.site.urls)),        
        url(r'^jsi18n/$', 'django.views.i18n.javascript_catalog', js_info_dict)
    )

if settings.ENABLE_OPENID:
    urlpatterns += patterns('',    
        url(r'^openid/', include('django_authopenid.urls'))
    )
        
urlpatterns += staticfiles_urlpatterns()
