from django.conf.urls.defaults import patterns, url
from djangopm import views

urlpatterns = patterns('',
    url(r'^$', views.home, name="pm_home"),
    url(r'^inbox/$', views.inbox, name="pm_inbox"),
    url(r'^outbox/$', views.outbox, name="pm_outbox"),
    url(r'^draftbox/$', views.draftbox, name="pm_draftbox"),
    url(r'^inbox/detail/(?P<id>[\d]+)/$', views.inbox_detail, name="pm_detail_in"),
    url(r'^outbox/detail/(?P<id>[\d]+)/$', views.outbox_detail, name="pm_detail_out"),
    url(r'^draftbox/detail/(?P<id>[\d]+)/$', views.message_detail, name="pm_detail"),
    url(r'^inbox/delete/$', views.message_delete, name="pm_inbox_delete"),
    url(r'^outbox/delete/$', views.message_delete, name="pm_outbox_delete", kwargs = {'type': 'outbox'}),
    url(r'^draftbox/delete/$', views.message_delete, name="pm_draftbox_delete", kwargs = {'type': 'draftbox'}),
    url(r'^compose/reply/(?P<id>[\d]+)/$', views.message_reply, name="pm_reply"),
    url(r'^compose/replyall/(?P<id>[\d]+)/$', views.message_reply, name="pm_reply_all", kwargs = {'all': True}),
    url(r'^compose/$', views.message_submit, name="pm_compose"),
)
