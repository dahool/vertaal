# -*- coding: utf-8 -*-
"""Copyright (c) 2014 Sergio Gabriel Teves
All rights reserved.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""

import datetime, time
from models import MigrationToken
from django.conf import settings
from django.db.utils import IntegrityError
from django.utils.crypto import salted_hmac

def link_user_account(token):
    try:
        m = MigrationToken.objects.get(pk=token, used=False)
        meta_diff = datetime.datetime.now() - datetime.timedelta(days=getattr(settings, 'MIG_EXPIRES', 2))
        if m.created >= meta_diff and m.user.is_active:
            associate_user_backend(m.user)
            m.used = True
            m.save()
            return m.user
    except MigrationToken.DoesNotExist:
        pass
    return None

def get_user_token(user):
    try:
        meta_diff = datetime.datetime.now() - datetime.timedelta(days=getattr(settings, 'MIG_EXPIRES', 2))
        m = MigrationToken.objects.filter(user=user, used=False, created__gte=meta_diff)
        if len(m) > 0:
            return m[0].token
    except MigrationToken.DoesNotExist:
        pass
    token = addNewToken(user)
    return token

def addNewToken(user):
    token = generate_token(user)
    try:
        MigrationToken.objects.create(token=token, user=user)
    except IntegrityError:
        token = addNewToken(user)
    return token
            
def generate_token(user):
    timestamp = str(time.time())
    key_salt = "openidmigration"+timestamp
    login_timestamp = user.last_login
    value = (unicode(user.id) + user.password + unicode(login_timestamp) + unicode(timestamp))
    return salted_hmac(key_salt, value).hexdigest()

def associate_user_backend(user):
    from django.contrib.auth import load_backend
    for backend in settings.AUTHENTICATION_BACKENDS:
        if user == load_backend(backend).get_user(user.pk):
            user.backend = backend
            break