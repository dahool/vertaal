#----- Evolution for openidmigration
from django_evolution.mutations import AddField
from django.db import models


MUTATIONS = [
    AddField('MigrationToken', 'used', models.BooleanField, initial=False)
]
#----------------------