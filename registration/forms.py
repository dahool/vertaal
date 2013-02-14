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
from django.contrib.auth.forms import *
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.forms.util import ErrorList
from common.forms import TipErrorList
 
class RegistrationForm(UserCreationForm):
    
    email = forms.EmailField(label=_("E-mail"))
    password1 = forms.CharField(label=_("Password"), widget=forms.PasswordInput(attrs={'autocomplete':'off'}))
    
    class Meta:
        model = User
        fields = ("username","email",)
        
    def werrors(self):
        """
        Returns an ErrorList for this field. Returns an empty ErrorList
        if there are none.
        """
        return TipErrorList(super(RegistrationForm, self)._get_errors())
            
    def clean_username(self):
        try:
            return super(RegistrationForm, self).clean_username()
        except:
            raise forms.ValidationError(_("The choosen username already exists."))
    
    def clean_email(self):
        """
        Validates already existing e-mail address.
        """
        email = self.cleaned_data.get("email")
        if not email:
            raise forms.ValidationError(_("This field is required."))
        self.users_cache = User.objects.filter(email__iexact=email)
        if len(self.users_cache) > 0:
            raise forms.ValidationError(_("That e-mail address already have an associated user account."))
        return email