#!/usr/bin/env bash
set -e

# Ejecutar migraciones solo si SKIP_MIGRATIONS no está activado
if [ "${SKIP_MIGRATIONS:-}" = "true" ]; then
    echo "SKIP_MIGRATIONS=true — skipping migrations."
else
    echo "Running Django migrations (prod settings)..."
    # Run migrations but do not abort the whole start script if they fail.
    # This prevents deploys from failing hard when the DB is temporarily
    # inaccessible or credentials/permissions are not yet correct.
    if python manage.py migrate --noinput --settings=config.settings.prod; then
        echo "Migrations completed successfully."
    else
        echo "WARNING: migrations failed — continuing startup. Check logs for details." >&2
    fi
fi

# Recoger archivos estáticos
echo "Collecting static files..."
python manage.py collectstatic --noinput --settings=config.settings.prod

# Crear superusuario si no existe — solo si CREATE_SUPERUSER_ON_START=true
# Además: no crear si SKIP_MIGRATIONS=true para evitar fallos cuando la BD no está lista
if [ "${SKIP_MIGRATIONS:-}" != "true" ] && [ "${CREATE_SUPERUSER_ON_START:-}" = "true" ]; then
    echo "Ensuring superuser exists..."
    python manage.py shell --settings=config.settings.prod <<'PY'
from django.contrib.auth import get_user_model
import os

User = get_user_model()
username = os.getenv('DJANGO_SUPERUSER_USERNAME')
email = os.getenv('DJANGO_SUPERUSER_EMAIL')
password = os.getenv('DJANGO_SUPERUSER_PASSWORD')

if username and password:
    if not User.objects.filter(username=username).exists():
        User.objects.create_superuser(username=username, email=email or '', password=password)
        print('Created superuser', username)
    else:
        print('Superuser already exists:', username)
else:
    print('DJANGO_SUPERUSER_USERNAME and DJANGO_SUPERUSER_PASSWORD must be set to create superuser')
PY
fi

echo "Starting gunicorn..."
exec gunicorn config.wsgi:application --bind 0.0.0.0:$PORT
