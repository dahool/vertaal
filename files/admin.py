from django.contrib import admin
from files.models import *

class POFileAdmin(admin.ModelAdmin):
    search_fields=['filename','slug']

class POTFileAdmin(admin.ModelAdmin):
    search_fields=['name']

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
                
admin.site.register(POFile,POFileAdmin)
admin.site.register(POTFile,POTFileAdmin)
admin.site.register(POFileLock, POFileLockAdmin)
admin.site.register(POFileSubmit, POFileSubmitAdmin)
admin.site.register(POFileLog, POFileLogAdmin)
admin.site.register(POFileAssign,POFileAssignAdmin)
admin.site.register(POTFileNotification,POTFileNotificationAdmin)
