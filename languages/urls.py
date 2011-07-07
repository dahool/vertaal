from django.conf.urls.defaults import *
from django.contrib import admin
from languages.models import Language

admin.autodiscover()

urlpatterns = patterns('django.views.generic',
    url(
        regex = '^(?P<slug>[-_@\w]+)/$',
        view = 'list_detail.object_detail',
        name = 'language_detail',
        kwargs = {'slug_field': 'code',
                  "template_object_name" : "language",
                  'queryset': Language.objects.all()}        
        ),
    url (
        name = 'language_list',
        regex = '^$',
        view = 'list_detail.object_list',
        kwargs = {"template_object_name" : "language",
                  'queryset': Language.objects.all()}
    )
)