# Django settings for pureftpman project.
import os
import glob

PROJECT_PATH = os.path.normpath(os.path.abspath(os.path.dirname(__file__)))

LOCAL_CONFIG = None
VERSION = None
ROOT_PATH = PROJECT_PATH

conffiles = glob.glob(os.path.join(os.path.dirname(__file__), 'settings','*.pyconf'))
conffiles.sort()

for f in conffiles:
    execfile(os.path.abspath(f)) 

if LOCAL_CONFIG and os.path.exists(LOCAL_CONFIG):
    execfile(LOCAL_CONFIG)
  
LOG_FILENAME = os.path.join(ROOT_PATH,'logs','vertaal.log')
ERROR_LOG_FILENAME = os.path.join(ROOT_PATH,'logs','error_vertaal.log')
BATCH_LOG_FILENAME = os.path.join(ROOT_PATH,'logs','bot_vertaal.log')
RPC_LOG_FILENAME = os.path.join(ROOT_PATH,'logs','rpc_vertaal.log')

TEMP_UPLOAD_PATH = os.path.join(ROOT_PATH, 'tmp')
UPLOAD_PATH = os.path.join(ROOT_PATH, 'uploads')
REPOSITORY_LOCATION = os.path.join(ROOT_PATH, 'files')
BUILD_LOG_PATH = os.path.join(ROOT_PATH, 'build_logs')
