#!/bin/bash
set -e

echo "==> Collecting static files..."
python manage.py collectstatic --noinput

echo "==> Running database migrations..."
python manage.py migrate

echo "==> Importing research data..."
python manage.py import_research

echo "==> Starting Gunicorn..."
exec gunicorn endorbit.wsgi --bind 0.0.0.0:8000 --workers 2 --timeout 120
