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
from files.models import *

class POFileAdmin(admin.ModelAdmin):
    search_fields=['filename','slug']

class POTFileAdmin(admin.ModelAdmin):
    search_fields=['name']
    readonly_fields = ('pofiles',)
    
class POTFileNotificationAdmin(admin.ModelAdmin):
    search_fields=['pofile__filename', 'potfile__name']
    
class POFileAssignAdmin(admin.ModelAdmin):
    search_fields=['pofile__filename', 'translate__username', 'review__username']
    list_display = ['pofile', 'translate','review']
    list_editable=['translate','review']

class POFileLockAdmin(admin.ModelAdmin):
    search_fields=['pofile__filename', 'owner__username']
    list_display = ['pofile', 'owner']
    list_editable=['owner']

class POFileLogAdmin(admin.ModelAdmin):
    search_fields=['pofile__filename', 'pofile__slug']

class POFileSubmitAdmin(admin.ModelAdmin):
    readonly_fields = ('pofile',)
    search_fields=['pofile__filename', 'pofile__slug']
                
admin.site.register(POFileSubmitSet)           
admin.site.register(POFile,POFileAdmin)
admin.site.register(POTFile,POTFileAdmin)
admin.site.register(POFileLock, POFileLockAdmin)
admin.site.register(POFileSubmit, POFileSubmitAdmin)
admin.site.register(POFileLog, POFileLogAdmin)
admin.site.register(POFileAssign,POFileAssignAdmin)
admin.site.register(POTFileNotification,POTFileNotificationAdmin)
