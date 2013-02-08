from django.conf.urls.defaults import patterns, url
from projects import views 

urlpatterns = patterns('',
    url(r'^add/$', views.project_create_update, name = 'project_create'),
    url(r'^(?P<slug>[-\w]+)/edit/$', views.project_create_update, name = 'project_edit'),
    url(r'^(?P<slug>[-\w]+)/delete/$', views.project_delete, name = 'project_delete'),
    url(r'^(?P<release_slug>[-\w]+)/build/$', views.project_build, name = 'project_build'),
    url(r'^(?P<slug>[-\w]+)/$', views.project_detail, name = 'project_detail'),
    url(r'^$', views.project_list, name = 'project_list'),                       
)