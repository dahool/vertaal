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
from news.models import *
from django.conf import settings

class ArticleForm(forms.ModelForm):
    
    title = forms.CharField(widget=forms.TextInput(attrs={'size':60}),
                              label=_('Title'))

#    translation = forms.CharField(widget=forms.TextInput(attrs={'size':50}),
#                                  help_text=_('Recommended translations'),
#                                  label=_('Translation'))
#    comment = forms.CharField(required=False,
#                              widget=forms.TextInput(attrs={'size':60}),
#                              label=_('Comments'))
#
#    def __init__(self, *args, **kwargs):
#        super(GlossaryForm, self).__init__(*args, **kwargs)
#        instance = getattr(self, 'instance', None)
#        if instance and instance.id:
#            self.fields['word'].widget.attrs['readonly'] = True
#    
    class Meta:
        model = Article
        exclude = ('author',)

    def save(self, user, commit=True):
        elem = super(ArticleForm, self).save(commit=False)
        elem.author = user
        if commit:
            elem.save()
        return elem