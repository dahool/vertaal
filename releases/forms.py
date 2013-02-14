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
import re

from django import forms
from releases.models import *
from django.conf import settings

class ReleaseForm(forms.ModelForm):

    class Meta:
        model = Release
        
    def clean_vcsbranch(self):
        path = self.cleaned_data.get("vcsbranch")
        if settings.PATH_RE:
            if path:
                path = re.sub(settings.PATH_RE, '', path) 
        return path