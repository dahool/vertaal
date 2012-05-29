from django.conf.urls.defaults import patterns, url, include
from django.contrib import admin
from teams.models import *
from teams.views import * 

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^add-member/(?P<teamid>[-\w]+)/$',
        add_member,
        name="add_member"),
    url(r'^remove-member/(?P<teamid>[-\w]+)/(?P<userid>[-\w]+)/$',
        remove_member,
        name="remove_member"),
    url(r'^change-group/(?P<teamid>[-\w]+)/(?P<userid>[-\w]+)/(?P<group>[-\w]+)/$',
        update_group,
        name="change_group"),
    url(r'^remove-grant/(?P<teamid>[-\w]+)/(?P<userid>[-\w]+)/(?P<codename>[-\w]+)/$',
        update_permission,
        name="remove_grant",  kwargs = {'remove': True }),
    url(r'^add-grant/(?P<teamid>[-\w]+)/(?P<userid>[-\w]+)/(?P<codename>[-\w]+)/$',
        update_permission,
        name="add_grant"),
    url(
        regex = '^(?P<teamid>[-\w]+)/join/$',
        view = join_request,
        name = 'join_request',),
    url(
        regex = '^(?P<id>[-\w]+)/join-acccept/$',
        view = join_accept,
        name = 'join_accept',),
    url(
        regex = '^(?P<id>[-\w]+)/join-reject/$',
        view = join_accept,
        name = 'join_reject',
        kwargs = {'reject': True }),                
    url(
        regex = '^(?P<id>[-\w]+)/admin/$',
        view = team_admin,
        name = 'team_admin',),
    url(
        regex = '^(?P<id>[-\w]+)/contact/$',
        view = team_contact,
        name = 'team_contact',),        
    url(
        regex = '^(?P<project>[-\w]+)/(?P<lang>[-_@\w]+)/$',
        view = team_detail,
        name = 'team_detail',),
    url(
        regex = '^(?P<project>[-\w]+)/$',
        view = add_team,
        name = 'team_create',),        
)