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
from django.utils.translation import ugettext_lazy as _
from django import forms
from django.conf import settings

class UploadFileForm(forms.Form):
    file  = forms.FileField(error_messages={'required': _('Please select a file to upload.')})
    comment = forms.CharField(max_length=255)
    
    def clean_file(self):
        f = self.cleaned_data.get("file")
        if f.size > settings.MAX_FILE_SIZE:
            raise forms.ValidationError(_("File size too big."))
        return f

class FileEditForm(forms.Form):
    content = forms.CharField(widget=forms.widgets.Textarea(attrs={'rows':25, 'cols':150}),
                              error_messages={'required': _('You are trying to submit an empty file.')})
    comment = forms.CharField(max_length=255)
    
    def clean_content(self):
        # remove extra breaks added by post
        return re.sub('[\r]','',self.cleaned_data.get("content"))

class RejectSubmitForm(forms.Form):
    message = forms.CharField(label=_('Comments'))    
    
class CommentForm(forms.Form):
    message = forms.CharField(label=_('Comments'), required=False)    