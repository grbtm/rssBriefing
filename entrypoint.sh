#!/bin/bash
# Script based on https://pythonspeed.com/articles/schema-migrations-server-startup/
set -euo pipefail

# Only run database migration if environment variable is set
if [ -v DB_UPGRADE ]; then
    flask db upgrade
fi

# Populate database with seed user and feeds if environment variable is set
if [ -v DB_SEED ]; then
    flask seed-db
fi

# Always launch the gunicorn app server
exec gunicorn -b :5003 --workers=2 --threads=4 --worker-class=gthread --worker-tmp-dir /dev/shm application:application

