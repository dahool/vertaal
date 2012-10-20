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
"""
Created on 20/10/2012
"""
from django_evolution.mutations import AddField, ChangeField
from django.db import models

MUTATIONS = [
    AddField('POFileSubmit', 'status', models.IntegerField, initial=0, db_index=True),
    ChangeField('POFileSubmit', 'pofile', initial=0, null=False),
]