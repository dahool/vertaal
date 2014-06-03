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
from django.utils.translation import ugettext_lazy as _

class UserAuditLogAdmin(admin.ModelAdmin):
    search_fields=['username','ip']
    list_display = ['created', 'username','ip', 'action']

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    max_num = 1
    can_delete = False

class UserAdmin(AuthUserAdmin):
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
  
  
# unregister old user admin
admin.site.unregister(User)
# register new user admin
admin.site.register(User, UserAdmin)

admin.site.register(UserFile)
admin.site.register(Favorite)
admin.site.register(UserAuditLog,UserAuditLogAdmin)