#----- Evolution for files
from django_evolution.mutations import AddField
from django.db import models

MUTATIONS = [
    AddField('POFileSubmitDeferred', 'locked', models.BooleanField, initial=False, db_index=True)
]
#----------------------
