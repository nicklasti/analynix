#!/bin/sh
# Container entry point: migrate, start the data-update scheduler, serve the site.
set -e

python manage.py migrate --noinput

if [ "${RUN_SCHEDULER:-1}" = "1" ]; then
    # Unless a full update has finished in the last 6 days, run one now: a brand-new
    # database, or an update that a restart or redeploy cut short, is picked up again.
    python manage.py update_all --if-older-than 6 &
    python manage.py run_scheduler &
fi

exec gunicorn analynix.wsgi:application \
    --bind 0.0.0.0:8080 \
    --workers "${WEB_CONCURRENCY:-2}" \
    --threads 4 \
    --timeout 60 \
    --access-logfile -
