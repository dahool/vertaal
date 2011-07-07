from django.conf.urls.defaults import *
from userprofileapp.views import *

urlpatterns = patterns('',
    url(r'^$', account_profile, name="user_profile"),
    url(r'^startup/$', startup_redirect),                       
    url(r'^startup/set/$', set_startup, name="add_startup"),
    url(r'^startup/remove/$', set_startup, name="remove_startup", kwargs = {'remove': True }),
    url(r'^favorites/add/$', update_favorites, name="add_favorites"),
    url(r'^favorites/remove/$', update_favorites, name="remove_favorites", kwargs = {'remove': True }),
    url(r'^favorites/remove/profile$', update_favorites, name="profile_remove_fav", kwargs = {'remove': True, 'idtype': True}),
)
