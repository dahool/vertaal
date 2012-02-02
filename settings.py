# Django settings for vertaal project.
import os
import logging
import re

PROJECT_PATH = os.path.normpath(os.path.abspath(os.path.dirname(__file__)))

BLOCK_USER_AGENTS = (
    re.compile(r'MSIE'),
)

PATH_RE = '\A(/|\\\\)+|(/|\\\\)*\Z'

MAINTENANCE_MODE = False

BOT_USERNAME = 'bot'

DEBUG = False
TEMPLATE_DEBUG = DEBUG
STATIC_SERVE = False
LOG_LEVEL = logging.INFO
BATCH_LOG_LEVEL = LOG_LEVEL
RPC_LOG_LEVEL = LOG_LEVEL

ENABLE_RPC = False
BACKUP_UPLOADS = True
ENABLE_OPENID = True
ENABLE_RSS = False

PROJECT_NAME = 'Vertaal'
VERSION = '1.3.16'
VERSION_HIST = ('1.3.13','1.3.14','1.3.15',)

LANGUAGE_COOKIE_NAME = 'vertaal_language'

USE_CAPTCHA = True
CONTACT_USE_CAPTCHA = True
JOIN_USE_CAPTCHA = True

TEST_RUNNER = 'tests.test_runner.run_tests'

# COOKIE AGE FOR FILTER AND OTHERS. IN SECONDS
COMMON_COOKIE_AGE = 1296000 # 15 days

PAGINATION_DEFAULT_PAGINATION = 10
SHOW_LATEST_PROJECTS = 8
MESSAGE_DAYS_AGE = 15
LOG_EXCEPTION_DB = True
AUTO_UNLOCK_BUILD = 30 # in minutes

INTERNAL_IPS = ('127.0.0.1',)

FEED_CACHE = 7200

ADMINS = (
    ('Administrator', 'admin@vertaal.com.ar'),
)

MANAGERS = ADMINS

ADMIN_USER = 'admin'

DATABASES = {
    'default': {
        'NAME': 'vertaal.db.sqlite',
        'ENGINE': 'django.db.backends.sqlite3',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
    },
}

EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = '-'
EMAIL_HOST_PASSWORD = '-'
EMAIL_USE_TLS = True
EMAIL_SUBJECT_PREFIX = '[Vertaal] '
DEFAULT_FROM_EMAIL = EMAIL_SUBJECT_PREFIX + '<noreply@vertaal.com.ar>'

# -*- CACHE -*- 
CACHE_BACKEND ="dummy://"
CACHE_MIDDLEWARE_SECONDS = 60 * 15
CACHE_MIDDLEWARE_KEY_PREFIX = 'vertaal'
CACHE_MIDDLEWARE_ANONYMOUS_ONLY = True

# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

LANGUAGES = (
    ('pt_BR', 'Brazilian Portuguese'),             
    ('en', 'English'),
    ('fr', 'French'),
    ('de', 'German'),
    ('gl', 'Galician'),
    ('it', 'Italian'),
    ('es', 'Spanish'),    
)

# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
#TIME_ZONE = 'America/Argentina/Buenos_Aires'
TIME_ZONE = 'UTC'

SITE_ID = 1

SITE_DOMAIN = 'localhost:8000'

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

TICKET_URL = 'http://code.google.com/p/vertaal/issues'

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(PROJECT_PATH, 'site_store')
STATIC_ROOT = os.path.join(PROJECT_PATH, 'media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/site_store/'
STATIC_URL = '/media/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = STATIC_URL + 'admin/'

LOGIN_URL = '/accounts/signin/'
LOGOUT_REDIRECT_URL = '/'
LOGIN_REDIRECT_URL = '/profile/startup'
#STARTUP_REDIRECT_URL = '/profile'
STARTUP_REDIRECT_URL = '/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = r"[[SECRETKEY]]"

# List of callables that know how to import templates from various sources.
#TEMPLATE_LOADERS = (
#    'django.template.loaders.filesystem.load_template_source',
#    'django.template.loaders.app_directories.load_template_source',
##     'django.template.loaders.eggs.load_template_source',
#)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.core.context_processors.request',
    #'django.contrib.messages.context_processors.messages',
    'django_authopenid.context_processors.authopenid',
)

MIDDLEWARE_CLASSES = (
    'common.middleware.agentdetect.AgentRejectMiddleware',                            
    'django.middleware.cache.UpdateCacheMiddleware',
    'django.middleware.gzip.GZipMiddleware',
#    'debug_toolbar.middleware.DebugToolbarMiddleware',
    #'django.contrib.messages.middleware.MessageMiddleware',                      
    'django.contrib.sessions.middleware.SessionMiddleware',
    #'django_openidconsumer.middleware.OpenIDMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.common.CommonMiddleware',
    'userprofileapp.middleware.UserLocaleMiddleware',
    'auditor.middleware.AuditMiddleware',
    'django.middleware.cache.CacheMiddleware', ## use for CACHE_ANON_ONLY
    #'django.middleware.locale.LocaleMiddleware',
    'maintenancemode.middleware.MaintenanceModeMiddleware',
    'pagination.middleware.PaginationMiddleware',
    'exceptionlogger.middleware.ExceptionLoggerMiddleware',
    'common.middleware.http.HttpErrorMiddleware',
    'django_authopenid.middleware.OpenIDMiddleware',
    'django.middleware.cache.FetchFromCacheMiddleware',
)

AUTH_PROFILE_MODULE = 'userprofileapp.UserProfile'

ROOT_URLCONF = 'urls'

TEMPLATE_DIRS = (
    os.path.join(PROJECT_PATH, 'templates'),
)

INSTALLED_APPS = (
    #'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.auth',
    'django.contrib.admin',     
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.markup',
    'django_evolution',
    'django_authopenid',
    #'django_openidconsumer',
    'app',
    'vertaalevolve',
    'auditor',
    'projects',
    'releases',
    'components',
    'files',
    'languages',
    'registration',
    'contact',
    'teams',
    'userprofileapp',
    'versioncontrol',
    'timezones',
    'pagination',
    'maintenancemode',
    'glossary',
    'appfeeds',
    'notifications',
    'exceptionlogger',
    'news',
#    'debug_toolbar',
)
#
#OPENID_SREG = {
#    'optional': 'nickname',
#    'optional': 'email',
#    'optional': 'timezone',
#    'optional': 'language',
#    'optional': 'fullname'
#}

REPOSITORIES = (
                ('svn','subversion'),
                #('git','git'),
                )

XMLRPC_METHODS = (
    #('desktop.server.views.do_test', 'do_test',),
)
XMLRPC_VIEWS = (
    'rpc.views',
)

ROOT_PATH = PROJECT_PATH

try:
    execfile(os.path.join(PROJECT_PATH,'settings_local.py'))
except IOError:
    pass 

FILE_UPLOAD_PERMISSIONS = 0644
MAX_FILE_SIZE = 1048576

LOG_FILENAME = os.path.join(ROOT_PATH,'logs','vertaal.log')
ERROR_LOG_FILENAME = os.path.join(ROOT_PATH,'logs','error_vertaal.log')
BATCH_LOG_FILENAME = os.path.join(ROOT_PATH,'logs','bot_vertaal.log')
RPC_LOG_FILENAME = os.path.join(ROOT_PATH,'logs','rpc_vertaal.log')

TEMP_UPLOAD_PATH = os.path.join(ROOT_PATH, 'tmp')
UPLOAD_PATH = os.path.join(ROOT_PATH, 'uploads')
REPOSITORY_LOCATION = os.path.join(ROOT_PATH, 'files')
BUILD_LOG_PATH = os.path.join(ROOT_PATH, 'build_logs')