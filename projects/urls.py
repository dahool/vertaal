from django.conf.urls.defaults import *
from django.contrib import admin
from projects.models import Project
from projects.views import * 

admin.autodiscover()

#project_list = {
#    'queryset': Project.objects.all(),
#    'template_object_name': 'project',
#}

urlpatterns = patterns('',
    url(
        regex = '^add/$',
        view = project_create_update,
        name = 'project_create'),
    url(
        regex = '^(?P<slug>[-\w]+)/edit/$',
        view = project_create_update,
        name = 'project_edit',),
    url(
        regex = '^(?P<slug>[-\w]+)/delete/$',
        view = project_delete,
        name = 'project_delete',),
    url(
        regex = '^(?P<release_slug>[-\w]+)/build/$',
        view = project_build,
        name = 'project_build',),
) 

urlpatterns += patterns('django.views.generic',
    url(
        regex = '^(?P<slug>[-\w]+)/$',
        view = project_detail,
        name = 'project_detail'),
    url (
        regex = '^$',
        view = project_list,
        name = 'project_list'),
)