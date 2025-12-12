#!/usr/bin/env bash
set -e

if [ "${SKIP_MIGRATIONS:-}" = "true" ]; then
	echo "SKIP_MIGRATIONS=true — skipping migrations."
else
	echo "Running Django migrations (prod settings)..."
	python manage.py migrate --noinput --settings=config.settings.prod
fi

echo "Collecting static files..."
python manage.py collectstatic --noinput --settings=config.settings.prod

echo "Starting gunicorn..."
exec gunicorn config.wsgi:application --bind 0.0.0.0:$PORT
