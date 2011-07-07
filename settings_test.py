import os
import tempfile
from django.conf import settings

AUDIT_MODEL = False
ENABLE_RPC = False

TEST_REPO = os.path.join(settings.PROJECT_PATH,'test_repo','svn')

PID = str(os.getpid())
TEMP_PATH = os.path.join(tempfile.gettempdir(),"TEST_PATH_" + PID)

REPOSITORY_LOCATION = os.path.join(TEMP_PATH,'TEST_REPO')
 
TEMP_REPO_PATH = os.path.join(TEMP_PATH,'TEMP_REPO')

temp_repo = "file:///" + TEMP_REPO_PATH
TEMP_REPO = temp_repo.replace('\\','/')