#!/usr/bin/env sh
set -e

python manage.py migrate --noinput
python manage.py seed_gate_data
python manage.py collectstatic --noinput
gunicorn gateadvisor.wsgi:application --bind 0.0.0.0:${PORT:-8000}
