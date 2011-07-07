#----- Evolution for projects
from django_evolution.mutations import *
from django.db import models

MUTATIONS = [
    AddField('Project', 'repo_type', models.CharField, initial=u'svn', max_length=20)
]
#----------------------