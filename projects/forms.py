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
from django.forms import widgets
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from projects.models import *

from django.core.validators import URLValidator

userChoices = [(u.id, u.username) for u in User.objects.filter(is_active=True)]

class ProjectForm(forms.ModelForm):

    #vcsurl = forms.URLField(widget=widgets.TextInput(attrs={'size':'50'}),
                            #label=_('Repository URL'),
                            #help_text=_("Subversion repository URL"))
    vcsurl = forms.CharField(widget=widgets.TextInput(attrs={'size':'50'}),
                            label=_('Repository URL'),
                            help_text=_("Subversion repository URL"))                            
    viewurl = forms.URLField(widget=widgets.TextInput(attrs={'size':'50'}),
                            label=_('View Repository URL'),required=False)    
    repo_user = forms.RegexField(label=_("Username"), max_length=50,
                                 required=False,
                                 regex=r"^[-!\"#$%&'()*+,./:;<=>?@[\\\]_`{|}~a-zA-Z0-9]+$",
                                 help_text=_("Some repositories requires authentication to perform checkout."),
                                 error_message = _("Non ascii chars are forbidden."))
    password = forms.RegexField(label=_("Password"),
                                widget=widgets.PasswordInput(attrs={'autocomplete':'off'}),
                                required=False,
                                max_length=50,
                                regex=r"^[-!\"#$%&'()*+,./:;<=>?@[\\\]_`{|}~a-zA-Z0-9]+$",
                                error_message = _("Non ascii chars are forbidden."),
                                initial='')
    description = forms.CharField(widget=forms.TextInput(attrs={'size':'50'}),help_text=_("A short Description"))
    
    maintainers = forms.MultipleChoiceField(label=_("Project maintainers"),
                                            choices=userChoices)
    def clean_vcsurl(self):
        data = self.cleaned_data['vcsurl']
        if data:
            if not data.startswith('file://'):
                validate = URLValidator()
                validate(data)
        return data
        
    class Meta:
        model = Project
        exclude = ("repo_pwd", )

    def save(self, commit=True):
        project = super(ProjectForm, self).save(commit=False)
        rp = self.cleaned_data['password']
        if rp and rp <> '':
            project.set_repo_pwd(rp)
        if project.repo_user == '':
            project.repo_pwd = '' 
        if commit:
            project.save()
            self.save_m2m()
        return project
