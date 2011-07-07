from django import forms
from django.forms import widgets
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from projects.models import *

userChoices = [(u.id, u.username) for u in User.objects.filter(is_active=True)]

class ProjectForm(forms.ModelForm):

    vcsurl = forms.URLField(widget=widgets.TextInput(attrs={'size':'50'}),
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