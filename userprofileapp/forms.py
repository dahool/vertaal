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
from django.contrib.auth.models import User
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.forms.util import ErrorList
from timezones.forms import TimeZoneField
from common.forms import TipErrorList
from django.conf import settings

LANGUAGE_CHOICES = (('', _('<Browser defined>')),) + settings.LANGUAGES

class UserProfileForm(forms.ModelForm):
    
    email = forms.EmailField(label=_('E-mail'))
    new_password1 = forms.CharField(required=False,label=_("New password"), widget=forms.PasswordInput)
    new_password2 = forms.CharField(required=False,label=_("New password confirmation"), widget=forms.PasswordInput)
    old_password = forms.CharField(required=False,label=_("Old password"), widget=forms.PasswordInput)
    timezone = TimeZoneField(required=False, label=_('Time Zone'))
    language = forms.ChoiceField(required=False,label=_("Preferred language"), choices=LANGUAGE_CHOICES)

    def __init__(self, *args, **kw):
        if kw.has_key('instance'):
            val = {}
            if kw.has_key('initial'):
                val = kw['initial']
            obj = kw['instance']
            p = obj.get_profile()
            val['timezone']=p.timezone
            val['language']=p.language
            kw['initial']=val
        super(UserProfileForm, self).__init__(*args, **kw)
            
    class Meta:
        model = User
        fields = ("first_name", "last_name", "email",)
        
    def clean(self):
        old_password = self.cleaned_data.get('old_password')
        password1 = self.cleaned_data.get('new_password1')

        if old_password and not password1:
            self._errors["new_password1"] = ErrorList([_('Please, type the new password.')])
            del self.cleaned_data["new_password1"]
             
        return self.cleaned_data
        
    def clean_old_password(self):
        """
        Validates that the old_password field is correct.
        """
        old_password = self.cleaned_data.get('old_password')
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        
        if password1 and not old_password:
            raise forms.ValidationError(_("Please, type your current password."))

        if old_password:
            if not self.instance.check_password(old_password):
                raise forms.ValidationError(_("Your old password is incorrect. Please enter it again."))
        return old_password    
    
    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')

        if password1 and not password2:
            raise forms.ValidationError(_("You must confirm the new password."))
        
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError(_("The two password fields didn't match."))
        return password2

    def clean_email(self):
        """
        Validates already existing e-mail address.
        """
        email = self.cleaned_data.get("email")
        if not email:
            raise forms.ValidationError(_("This field is required."))
        filter = User.objects.filter(email__iexact=email)
        self.users_cache = filter.exclude(pk=self.instance.pk)
        if len(self.users_cache) > 0:
            raise forms.ValidationError(_("That e-mail address already have an associated user account."))        
        return email

    def save(self, commit=True):
        user = super(UserProfileForm, self).save(commit=False)
        if self.cleaned_data.get('new_password1'):
            user.set_password(self.cleaned_data.get('new_password1'))
        if self.cleaned_data.get('timezone'):
            p = user.get_profile()
            p.timezone = self.cleaned_data.get('timezone')
            p.save()
        if self.cleaned_data.get('language'):
            p = user.get_profile()
            p.language = self.cleaned_data.get('language')
            p.save()
        else:
            p = user.get_profile()
            p.language = None
            p.save()
        if commit:
            user.save()
        return user