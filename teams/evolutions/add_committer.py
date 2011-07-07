#----- Evolution for teams
from django_evolution.mutations import *
from django.db import models

MUTATIONS = [
    AddField('Team', 'committers', models.ManyToManyField, null=True, related_model='auth.User')
]
#----------------------