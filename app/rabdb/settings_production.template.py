"""
Django production settings for rabdb project.

"""

from .settings import *
from urllib.parse import urlparse

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = ''

DEBUG = False

ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    'rabdb',
    'rabdb.igc.gulbenkian.pt',
    'rabdb.org',
    'www.rabdb.org'
]

ADMINS = (
    ('Jaroslaw Surkont', 'jsurkont@igc.gulbenkian.pt'),
)

# BROKER_URL = ''
# CELERY_RESULT_BACKEND = ''
# CELERY_TASK_RESULT_EXPIRES = 3600 * 24 * 7

db_url = urlparse(os.environ.get('RABDB_DATABASE', 'postgresql://localhost:5432/rabdb'))
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.{:s}'.format(db_url.scheme),
        'NAME': db_url.path.strip('/'),
        'USER': db_url.username,
        'PASSWORD': db_url.password,
        'HOST': db_url.hostname,
        'PORT': str(db_url.port),
    }
}

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = ''
DEFAULT_FROM_EMAIL = ''
SERVER_EMAIL = ''
