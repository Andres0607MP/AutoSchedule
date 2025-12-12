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
    # Normalize known alternate schemes (e.g. Render may provide a mariadb:// URL)
    db_url = os.getenv('DATABASE_URL') or ''
    if db_url.startswith('mariadb://'):
        # dj_database_url expects mysql:// for MySQL-compatible backends
        db_url = 'mysql://' + db_url[len('mariadb://'):]
    DATABASES = {
        'default': dj_database_url.parse(db_url, conn_max_age=600)
    }
