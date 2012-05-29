from django.conf.urls.defaults import patterns, url, include
from django.contrib import admin
from glossary.views import *

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^(?P<project>[-\w]+)/(?P<lang>[-_@\w]+)/list/$', show_all, name="gloss_list"),
    url(r'^(?P<project>[-\w]+)/(?P<lang>[-_@\w]+)/add/$',
        create_update, name="gloss_add"),
    url(r'^(?P<word_id>[0-9]+)/edit/$',
        create_update, name="gloss_edit"),
    url(r'^(?P<word_id>[0-9]+)/remove/$',
        remove_word, name="gloss_remove"),
    url(r'^(?P<word_id>[0-9]+)/log/$',
        show_log, name="gloss_log"),
    url(r'^select/$', language_selection, name="gloss_lang_selection"),
    url(r'^$', show_all, name="gloss_home"),
    url(r'^(?P<project>[-\w]+)/(?P<lang>[-_@\w]+)/export/$', export_tbx, name="export_tbx"),
)