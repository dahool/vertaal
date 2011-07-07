from django.db import models

class AppVersion(models.Model):
    version = models.CharField(max_length=10, db_index=True)
    created = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table  = 'app_version'
        ordering  = ('-created',)