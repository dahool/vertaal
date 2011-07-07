#----- Evolution for teams
from django_evolution.mutations import *
from django.db import models

MUTATIONS = [
    AddField('Team', 'submittype', models.IntegerField, initial=0, db_index=True)
]
#----------------------