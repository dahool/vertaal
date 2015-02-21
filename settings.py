import os
import glob

WSGI_APPLICATION='vertaal.wsgi.application'

#enforce old serializer to support openid
SESSION_SERIALIZER = 'django.contrib.sessions.serializers.PickleSerializer'

PROJECT_PATH = os.path.normpath(os.path.abspath(os.path.dirname(__file__)))

LOCAL_CONFIG = None
VERSION = None
ROOT_PATH = os.path.join(PROJECT_PATH, 'appcache')

conffiles = glob.glob(os.path.join(PROJECT_PATH, 'settings','*.pyconf'))
conffiles.sort()

for f in conffiles:
    execfile(os.path.abspath(f)) 

FQDN = "https://%s" % SITE_DOMAIN

LOG_PATH = os.path.join(ROOT_PATH,'logs')
LOG_FILENAME = os.path.join(LOG_PATH,'vertaal.log')
ERROR_LOG_FILENAME = os.path.join(LOG_PATH,'error_vertaal.log')
BATCH_LOG_FILENAME = os.path.join(LOG_PATH,'bot_vertaal.log')
COMMAND_LOG_FILENAME = os.path.join(LOG_PATH,'cmd_vertaal.log')
RPC_LOG_FILENAME = os.path.join(LOG_PATH,'rpc_vertaal.log')

TEMP_UPLOAD_PATH = os.path.join(ROOT_PATH, 'tmp')
UPLOAD_PATH = os.path.join(ROOT_PATH, 'uploads')
REPOSITORY_LOCATION = os.path.join(ROOT_PATH, 'files')
BUILD_LOG_PATH = os.path.join(ROOT_PATH, 'build_logs')

version_file = os.path.join(PROJECT_PATH, 'buildinfo')
if os.path.exists(version_file):
    import datetime
    BUILD_VERSION = datetime.datetime.fromtimestamp(os.path.getmtime(version_file)).strftime('%Y%m%d')
    
if LOCAL_CONFIG and os.path.exists(LOCAL_CONFIG):
    execfile(LOCAL_CONFIG)
    
# FIX PATHS
for checkpath in (LOG_PATH, TEMP_UPLOAD_PATH, UPLOAD_PATH, REPOSITORY_LOCATION, BUILD_LOG_PATH):
    if not os.path.exists(checkpath):
        try:
            os.makedirs(checkpath)
        except:
            pass