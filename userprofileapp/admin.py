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
from django.contrib import admin
from userprofileapp.models import *

from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin
from django.utils.translation import ugettext, ugettext_lazy as _

from django.core import urlresolvers
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.http import HttpResponseRedirect
        
class UserAuditLogAdmin(admin.ModelAdmin):
    search_fields=['username','ip']
    list_display = ['created', 'username','ip', 'action']

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    max_num = 1
    can_delete = False

class UserAdmin(AuthUserAdmin):
    change_form_template = 'admin/auth/user/change_form.html'

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), { 'classes': ('grp-collapse grp-closed',),
                             'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    
    def add_view(self, *args, **kwargs):
        self.inlines = []
        return super(UserAdmin, self).add_view(*args, **kwargs)

    def change_view(self, *args, **kwargs):
        self.inlines = [UserProfileInline]
        return super(UserAdmin, self).change_view(*args, **kwargs)
  
    def get_urls(self):
        from django.conf.urls import patterns, url
        return patterns('',
            url(r'^(\d+)/passwordreset/$',
            self.admin_site.admin_view(self.user_password_reset), name='%s_%s_passwordreset' % (self.model._meta.app_label, self.model._meta.model_name))
        ) + super(UserAdmin, self).get_urls()
  
    def user_password_reset(self, request, id, form_url=''):
        from django.contrib.auth.tokens import default_token_generator
        from django.contrib.auth.forms import PasswordResetForm
        
        if not self.has_change_permission(request):
            raise PermissionDenied
        user = get_object_or_404(self.get_queryset(request), pk=id)
        post_reset_redirect = urlresolvers.reverse('admin:%s_%s_change' % (self.model._meta.app_label, self.model._meta.model_name), args=(id,))

        form = PasswordResetForm({'email': user.email})
        if form.is_valid():
            opts = {
                'use_https': request.is_secure(),
                'token_generator': default_token_generator,
                'from_email': None,
                'email_template_name': 'registration/password_reset_email.html',
                'subject_template_name': 'registration/password_reset_subject.txt',
                'request': request,
            }
            opts = dict(opts, domain_override=request.get_host())
            form.save(**opts)

            msg = ugettext('Password reset link sent.')
            messages.success(request, msg)
        else:
            msg = ugettext('Error ocurred while sending password reset link.')
            messages.error(request, msg)
        
        return HttpResponseRedirect(post_reset_redirect)
  
# unregister old user admin
admin.site.unregister(User)
# register new user admin
admin.site.register(User, UserAdmin)

admin.site.register(UserFile)
admin.site.register(Favorite)
admin.site.register(UserAuditLog,UserAuditLogAdmin)