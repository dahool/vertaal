#----- Evolution for versioncontrol
from django_evolution.mutations import *
from django.db import models

MUTATIONS = [
    AddField('BuildCache', 'locked', models.BooleanField, initial=False),
    AddField('BuildCache', 'lock_expires', models.DateTimeField, null=True),
    DeleteField('BuildCache', 'lock')
]
#----------------------