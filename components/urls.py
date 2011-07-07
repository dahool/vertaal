from django.conf.urls.defaults import *
from django.contrib import admin
from components.models import Component
from components.views import *

admin.autodiscover()

component_list = {
    'queryset': Component.objects.all(),
    'template_object_name': 'component',
}

urlpatterns = patterns('',
    url(
        regex = '^(?P<project>[-\w]+)/add/$',
        view = component_create_update,
        name = 'component_create'),
    url(
        regex = '^(?P<slug>[-\w]+)/edit/$',
        view = component_create_update,
        name = 'component_edit',),
    url(
        regex = '^(?P<slug>[-\w]+)/delete/$',
        view = component_delete,
        name = 'component_delete',),
) 

urlpatterns += patterns('django.views.generic',
    url(
        regex = '^(?P<slug>[-\w]+)/$',
        view = component_detail,
        name = 'component_detail',),
#    url(
#        regex = '^(?P<project>[-\w]+)/(?P<release>[-\w]+)/(?P<component>[-\w]+)/log/$',
#        view = build_log,
#        name = 'build_log',),        
)

