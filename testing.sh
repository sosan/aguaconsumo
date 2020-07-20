#!/bin/sh
set -e
if [ "${FLASK_ENV}" = "development" ]; then
    echo "FLASK_ENV POR DEFECTO: development PORT=${PORT}"
    # exec "$@"
else
    echo "FLASK_ENV POR DEFECTO: production PORT=${PORT}"
    # exec gunicorn -b 0.0.0.0:${PORT} app
fi

exec "$@"

# shell_check myscript
# No issues detected!