from django.conf.urls.defaults import patterns, url
from contact import views
from django.conf import settings

urlpatterns = patterns('',
    url(r'^(?P<username>[\w.@+-]+)/$', views.contact, name="contact_me"),
    url(r'^$', views.contact, {'username': settings.ADMIN_USER}, name="contact_form", ),
)
