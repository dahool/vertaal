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