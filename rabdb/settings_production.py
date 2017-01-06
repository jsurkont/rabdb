"""
Django production settings for rabdb project.

"""

from .settings import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = ''

# SECURITY WARNING: don't run with debug turned on in production!
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

# Celery settings

BROKER_URL = ''
CELERY_RESULT_BACKEND = ''
CELERY_TASK_RESULT_EXPIRES = 3600 * 24 * 7

# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': '',
        'USER': '',
        'PASSWORD': '',
        'HOST': 'localhost',
        'PORT': '',
    }
}

# Email

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = ''
DEFAULT_FROM_EMAIL = ''
SERVER_EMAIL = ''