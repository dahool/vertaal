from django import forms
from django.utils.translation import ugettext as _
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