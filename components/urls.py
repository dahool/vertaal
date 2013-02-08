from django.conf.urls.defaults import patterns, url
from components import views

urlpatterns = patterns('',
    url(
        regex = '^(?P<project>[-\w]+)/add/$',
        view = views.component_create_update,
        name = 'component_create'),
    url(
        regex = '^(?P<slug>[-\w]+)/edit/$',
        view = views.component_create_update,
        name = 'component_edit',),
    url(
        regex = '^(?P<slug>[-\w]+)/delete/$',
        view = views.component_delete,
        name = 'component_delete',),
    url(
        regex = '^(?P<slug>[-\w]+)/$',
        view = views.component_detail,
        name = 'component_detail',),
) 