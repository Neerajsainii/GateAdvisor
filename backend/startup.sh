#!/usr/bin/env sh
set -e

python manage.py migrate --noinput
if [ "${SEED_GATE_DATA_ON_STARTUP:-false}" = "true" ]; then
  python manage.py seed_gate_data --reset
fi
python manage.py collectstatic --noinput
gunicorn gateadvisor.wsgi:application --bind 0.0.0.0:${PORT:-8000}
