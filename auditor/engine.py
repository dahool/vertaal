# -*- coding: utf-8 -*-
"""Copyright (c) 2012 Sergio Gabriel Teves
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
from django.core import serializers
from auditor.models import Audit, ACTIONS

from common.middleware import threadlocal

def serial_data(instance):
    serializer = serializers.get_serializer("json")()
    return serializer.serialize(instance, ensure_ascii=False)
    
def auditor_save_callback(sender, **kwargs):
    if not isinstance(kwargs['instance'],Audit):
        user = threadlocal.get_current_user()
        if user and user.is_authenticated():
            obj = kwargs['instance']
            if kwargs['created'] is True:
                act = ACTIONS['ADDITION']
            else:
                act = ACTIONS['CHANGE']
            try:
                Audit.objects.create(object_id=obj.pk,
                            object_repr=repr(obj),
                            user=user,
                            action_flag=act,
                            object_type=obj.__class__)
            except:
                pass
    
def auditor_delete_callback(sender, **kwargs):
    if not isinstance(kwargs['instance'],Audit):
        user = threadlocal.get_current_user()
        if user and user.is_authenticated():
            obj = kwargs['instance']
            try:
                Audit.objects.create(object_id=obj.pk,
                            object_repr=repr(obj),
                            user=user,
                            action_flag=ACTIONS['DELETION'],
                            object_type=obj.__class__)
            except:
                pass