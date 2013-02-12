from django.conf.urls.defaults import patterns, url, include
from django.contrib import admin
from app import views

urlpatterns = patterns('',
    url(r'^log/(?P<file>[-\w_]+)/$', views.get_log, name='get_log'),
    url(r'^user_messages/$', views.messages, name='user_messages'),
) 
