#----- Evolution for projects
from django_evolution.mutations import *
from django.db import models

MUTATIONS = [
    AddField('Component', 'potlocation', models.CharField, max_length=50, null=True)
]
#----------------------