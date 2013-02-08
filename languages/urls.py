from django.conf.urls.defaults import patterns, url
from languages.models import Language
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView

urlpatterns = patterns('',
    url(r'^(?P<slug>[-_@\w]+)/$', DetailView.as_view(
                                queryset=Language.objects.all(), 
                                slug_field='code',
                                context_object_name='language', 
                                template_name='language/language_detail'),
        name = 'language_detail'),                       
    url(r'^$', ListView.as_view(
                                queryset=Language.objects.all(), 
                                context_object_name='language_list', 
                                template_name='language/language_list'),
        name = 'language_list'),
)