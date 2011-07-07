from django_evolution.mutations import *
from django.db import models

MUTATIONS = [
    AddField('Project', 'viewurlparams', models.CharField, max_length=100, null=
True)
]