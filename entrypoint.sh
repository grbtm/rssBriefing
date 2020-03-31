#!/bin/bash
# Script based on https://pythonspeed.com/articles/schema-migrations-server-startup/
set -euo pipefail

# Only run database migration if environment variable is set
if [ -v DB_UPGRADE ]; then
    flask db upgrade
fi

# Always launch the app
exec python application.py
