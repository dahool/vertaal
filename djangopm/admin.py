from django.contrib import admin
from djangopm.models import PMMessage, PMInbox, PMOutbox

admin.site.register(PMMessage)
admin.site.register(PMInbox)
admin.site.register(PMOutbox)
