from django.conf import settings
from django.conf.urls.defaults import patterns, url, include
from django.contrib.auth import views as auth_views
from registration.views import *
from django_authopenid.views import signin as openid_signin
from django.conf import settings

urlpatterns = patterns('',
    #url(r'^signin/$', auth_views.login, name="user_signin"),                       
    url(r'^signin/$', openid_signin, name="user_signin", kwargs={"template_name":"registration/login.html"}),
    url(r'^signout/$', auth_views.logout, {'next_page': settings.LOGOUT_REDIRECT_URL }, name="user_signout"),
    #url(r'^profile/$', account_profile, name="user_profile"),
    url(r'^signup/$', register, name="user_signup"),
    url(r'^query/$', query_user, name="user_query"),
    url(r'^password_reset/$', auth_views.password_reset, name="password_reset"),
    url(r'^password_reset/done/$', auth_views.password_reset_done),
    url(r'^reset/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$', auth_views.password_reset_confirm),
    url(r'^reset/done/$', auth_views.password_reset_complete),
    #url(r'^$', account_profile),
)  
