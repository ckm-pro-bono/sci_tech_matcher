import os

# environment variable settings
DEBUG = bool(os.environ.get('DEBUG', False))

if DEBUG:
	from .debug import *
else:
	from .base import *

LOGIN_REQUIRED = bool(os.environ.get('LOGIN_REQUIRED', True))

if LOGIN_REQUIRED:
    MIDDLEWARE = MIDDLEWARE + []

# Secret key
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', '-06$r!12)s8v-*6xc$580)m3_45^zteh*5#tt(h6za^w%^8v!u')

# Email
from .email import *

# DBs
DATABASES = { 'default': {
	'ENGINE' : 'django.db.backends.postgresql_psycopg2',
	'NAME': os.environ.get('DATABASE_NAME', 'un_webapp'),
	'USER': os.environ.get('DATABASE_USER', ''),
	'PASSWORD': os.environ.get('DATABASE_PASSWORD', ''),
	'HOST': os.environ.get('DATABASE_HOST','localhost'),
	'PORT': os.environ.get('DATABASE_PORT', ''),
	'CONN_MAX_AGE': 600,
	}
}

STATIC_ROOT = os.environ.get('STATIC_ROOT', '')
MEDIA_ROOT = os.environ.get('MEDIA_ROOT', os.path.join(BASE_DIR, 'applicant_uploads'))