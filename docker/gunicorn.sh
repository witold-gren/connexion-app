#!/bin/sh

set -o errexit
set -o pipefail
set -o nounset

/opt/venv/bin/gunicorn wsgi:app \
        --chdir /app \
        --name connexionapp \
        --bind ${GUNICORN_HOST:-0.0.0.0}:${GUNICORN_PORT:-5000} \
        --timeout ${GUNICORN_TIMEOUT:-300} \
        --workers ${GUNICORN_WORKERS:-1} \
        --worker-class ${GUNICORN_WORKER_CLASS:-sync} \
        --access-logfile ${GUNICORN_ACCESS_LOGFILE:--} \
        --error-logfile ${GUNICORN_ERROR_LOGFILE:--}
