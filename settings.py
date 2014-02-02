import os
import glob

PROJECT_PATH = os.path.normpath(os.path.abspath(os.path.dirname(__file__)))

LOCAL_CONFIG = None
VERSION = None
ROOT_PATH = os.path.join(PROJECT_PATH, 'appcache')

conffiles = glob.glob(os.path.join(os.path.dirname(__file__), 'settings','*.pyconf'))
conffiles.sort()

for f in conffiles:
    execfile(os.path.abspath(f)) 

LOG_FILENAME = os.path.join(ROOT_PATH,'logs','vertaal.log')
ERROR_LOG_FILENAME = os.path.join(ROOT_PATH,'logs','error_vertaal.log')
BATCH_LOG_FILENAME = os.path.join(ROOT_PATH,'logs','bot_vertaal.log')
COMMAND_LOG_FILENAME = os.path.join(ROOT_PATH,'logs','cmd_vertaal.log')
RPC_LOG_FILENAME = os.path.join(ROOT_PATH,'logs','rpc_vertaal.log')

TEMP_UPLOAD_PATH = os.path.join(ROOT_PATH, 'tmp')
UPLOAD_PATH = os.path.join(ROOT_PATH, 'uploads')
REPOSITORY_LOCATION = os.path.join(ROOT_PATH, 'files')
BUILD_LOG_PATH = os.path.join(ROOT_PATH, 'build_logs')

version_file = os.path.join(ROOT_PATH, 'buildinfo')
if os.path.exists(version_file):
    import datetime
    v = datetime.datetime.fromtimestamp(os.path.getmtime(version_file)).strftime('%Y%m%d')
    VERSION = VERSION + '-' + v

if LOCAL_CONFIG and os.path.exists(LOCAL_CONFIG):
    execfile(LOCAL_CONFIG)
    
