#----- Evolution for news
from django_evolution.mutations import AddField
from django.db import models

MUTATIONS = [
    AddField('Article', 'expires', models.DateField, null=True, db_index=True)
]
#----------------------