# -*- coding: utf-8 -*-
"""Copyright (c) 2013, Sergio Gabriel Teves
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

def get_user_model():
    "Return the User model that is active in this project"
    from django.conf import settings
    from django.db.models import get_model
    from django.core.exceptions import ImproperlyConfigured

    if getattr(settings, 'AUTH_USER_MODEL', None):
        try:
            app_label, model_name = settings.AUTH_USER_MODEL.split('.')
        except ValueError:
            raise ImproperlyConfigured("AUTH_USER_MODEL must be of the form 'app_label.model_name'")
        user_model = get_model(app_label, model_name)
        if user_model is None:
            raise ImproperlyConfigured("AUTH_USER_MODEL refers to model '%s' that has not been installed" % settings.AUTH_USER_MODEL)
        return user_model
    else:
        from django.contrib.auth.models import User
        return User