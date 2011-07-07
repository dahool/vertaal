#----- Evolution for projects
from django_evolution.mutations import *
from django.db import models

MUTATIONS = [
    AddField('Project', 'viewurl', models.URLField, max_length=200, null=True)
]