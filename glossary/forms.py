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
from django import forms
from django.utils.translation import ugettext_lazy as _
from glossary.models import *
from django.conf import settings

class GlossaryForm(forms.ModelForm):
    
    translation = forms.CharField(widget=forms.TextInput(attrs={'size':50}),
                                  help_text=_('Recommended translations'),
                                  label=_('Translation'))
    comment = forms.CharField(required=False,
                              widget=forms.TextInput(attrs={'size':60}),
                              label=_('Comments'))

    def __init__(self, *args, **kwargs):
        super(GlossaryForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        if instance and instance.id:
            self.fields['word'].widget.attrs['readonly'] = True
    
    class Meta:
        model = Glossary
        exclude = ("added","initial","language","project",)
        
    def save(self, project, language, commit=True):
        elem = super(GlossaryForm, self).save(commit=False)
        elem.project = project
        elem.language = language
        if commit:
            elem.save()
        return elem