import os.path
from files.models import *

for lock in POFileLock.objects.all():
    lock.pofile.assigns.create(translate=lock.owner)
