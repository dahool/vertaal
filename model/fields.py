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
from django.db.models import fields
from common.utils.slug import slugify

class AutoSlugField(fields.SlugField):
    def __init__(self, prepopulate_from, force_update = False, *args, **kwargs):
        self.prepopulate_from = prepopulate_from
        self.force_update = force_update
        super(AutoSlugField, self).__init__(*args, **kwargs)

    def pre_save(self, model_instance, add):
        if self.prepopulate_from:
            value = slugify(model_instance, self, getattr(model_instance, self.prepopulate_from), self.force_update)
        else:
            value = super(AutoSlugField, self).pre_save(model_instance, add)
        setattr(model_instance, self.attname, value)
        return value