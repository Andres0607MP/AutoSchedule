from .base import *  # noqa
import os
import dj_database_url

DEBUG = False
ALLOWED_HOSTS = os.getenv('DJANGO_ALLOWED_HOSTS', '*').split(',')

SKIP_MIGRATIONS = os.getenv('SKIP_MIGRATIONS', 'false') == 'true'

if SKIP_MIGRATIONS:
    # fallback DB to avoid connection errors
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
elif os.getenv('DATABASE_URL'):
    DATABASES = {
        'default': dj_database_url.parse(os.getenv('DATABASE_URL'), conn_max_age=600)
    }
