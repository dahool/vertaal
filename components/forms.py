import re

from django import forms
from components.models import *
from django.conf import settings

class ComponentForm(forms.ModelForm):

    class Meta:
        model = Component
        
    def clean_vcspath(self):
        path = self.cleaned_data.get("vcspath")
        if settings.PATH_RE:
            if path:
                path = re.sub(settings.PATH_RE, '', path) 
        return path
    
    def clean_format(self):
        path = self.cleaned_data.get("format")
        if settings.PATH_RE:
            if path:
                path = re.sub(settings.PATH_RE, '', path) 
        return path    