from django import forms
from django.utils.translation import ugettext as _
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