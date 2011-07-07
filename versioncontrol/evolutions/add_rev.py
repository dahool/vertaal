#----- Evolution for projects
from django_evolution.mutations import *
from django.db import models

MUTATIONS = [
    AddField('BuildCache', 'rev', models.CharField, max_length=10, null=True)
]
#----------------------