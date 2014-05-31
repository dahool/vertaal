# -*- coding: utf-8 -*-
# Copyright 2007, 2008,2009 by Benoît Chesneau <benoitc@e-engura.org>
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from django.conf.urls import patterns, url

# views
from django_authopenid import views as oid_views

urlpatterns = patterns('',
    url(r'^password/$',oid_views.password_change, name='openid_password_change'),

    # manage account registration
    url(r'^associate/complete/$', oid_views.complete_associate, name='user_complete_associate'),
    url(r'^associate/$', oid_views.associate, name='user_associate'),
    url(r'^dissociate/$', oid_views.dissociate, name='user_dissociate'),
    url(r'^register/$', oid_views.register, name='user_register'),
    url(r'^signin/complete/$', oid_views.complete_signin, name='user_complete_signin'),
    url(r'^signin/$', oid_views.signin, name='openid_signin'),
        
    # yadis uri
    url(r'^yadis.xrdf$', oid_views.xrdf, name='oid_xrdf'),
)
