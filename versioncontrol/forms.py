from django.utils.translation import ugettext_lazy as _
from django import forms

class HttpCredForm(forms.Form):
    user = forms.CharField(label=_('Username'))
    password = forms.CharField(label=_('Password'), widget=forms.PasswordInput())
    message = forms.CharField(label=_('Comments'), required=False)