import os
import tempfile
import logging

DEBUG = True
TEMPLATE_DEBUG = DEBUG
STATIC_SERVE = True
LOG_LEVEL = logging.DEBUG
BATCH_LOG_LEVEL = LOG_LEVEL
RPC_LOG_LEVEL = LOG_LEVEL

ENABLE_RPC = False

USE_CAPTCHA = False
CONTACT_USE_CAPTCHA = False
JOIN_USE_CAPTCHA = False

EMAIL_HOST = 'localhost'
EMAIL_PORT = 25
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_USE_TLS = False

V2G_DB_HOST = 'localhost'
V2G_DB_USER = 'root'
V2G_DB_PWD = 'root'
V2G_DB_NAME = 'poat_v2g'

DATABASES = {
    'default': {
        'NAME': 'vertaal',
        'ENGINE': 'django.db.backends.mysql',
        'USER': 'vertaal',
        'PASSWORD': 'vertaal',
        'HOST': '166.40.231.124',
    },
}

SITE_DOMAIN = 'localhost:8000'

#INSTALLED_APPS += (
#    'django_xmlrpc',
#    'rpc',
#)

if os.name == "posix":
	ROOT_PATH = '/home/gabriel/vertaal'
else:
	ROOT_PATH = 'C:\\tmp\\vertaal'

RECAPTCHA_PRIVATE_KEY = '-'
RECAPTCHA_PUBLIC_KEY = '6Lc4DgYAAAAAAIRab8YZmNKmn3Cd1zAsJq9Jxly5'

