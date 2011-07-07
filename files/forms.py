import re
from django.utils.translation import ugettext as _
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