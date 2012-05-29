from django.conf.urls.defaults import patterns, url, include
from django.contrib import admin
from news.views import *

admin.autodiscover()

urlpatterns = patterns('',
    url(
        regex = '^add/$',
        view = news_add,
        name = 'news_add'),
    url(
        regex = '^view/(?P<slug>[-\w]+)/$',
        view = news_view,
        name = 'news_view'),        
)