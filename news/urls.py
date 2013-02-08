from django.conf.urls.defaults import patterns, url
from django.contrib import admin
from django.views.generic.detail import DetailView
from news.models import Article

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^view/(?P<slug>[-\w]+)/$', DetailView.as_view(
                                queryset=Article.objects.all(), 
                                context_object_name='article'), name = 'news_view')
)