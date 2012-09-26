from django.contrib import admin
from deferredsubmit.models import POFileSubmitDeferred

class POFileSubmitDeferredAdmin(admin.ModelAdmin):
    search_fields=['filesubmit__pofile__filename']

admin.site.register(POFileSubmitDeferred,POFileSubmitDeferredAdmin)
