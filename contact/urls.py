from django.conf.urls.defaults import *
from contact.views import *
from django.conf import settings

urlpatterns = patterns('',
    url(r'^(?P<username>[\w.@+-]+)/$', contact, name="contact_me"),
    url(r'^$', contact, {'username': settings.ADMIN_USER}, name="contact_form", ),
)
