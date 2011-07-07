#----- Evolution for files
from django_evolution.mutations import *
from django.db import models

MUTATIONS = [
    AddField('POFile', 'potupdated', models.DateTimeField, null=True)
]
#----------------------