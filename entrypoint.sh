#!/bin/bash
# Script based on https://pythonspeed.com/articles/schema-migrations-server-startup/
set -euo pipefail

# Only run database migration if environment variable is set
if [ -v DB_UPGRADE ]; then
    flask db upgrade
fi

# Always launch the gunicorn app server
exec gunicorn -b :5000 --workers=2 --threads=4 --worker-class=gthread --worker-tmp-dir /dev/shm rssBriefing:rssbriefing_package

