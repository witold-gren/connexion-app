#!/bin/sh

set -o errexit
set -o pipefail
set -o nounset

cmd="$@"

counter=0
until flask check_db_connection; do
  >&2 echo 'PostgreSQL is unavailable (sleeping)...'
  sleep 1
  if [ $counter -gt "60" ]; then
    echo "Can't connect to PostgreSQL. Exiting."
    exit 1
  fi
  counter=$(expr $counter + 1)
done

>&2 echo 'PostgreSQL is up - continuing...'


# Run migration when you first time run this container in dev environment. Only for usage docker-compose.
CONTROL_FIRST_MIGRATION=~/.created_migration
if [ ! -f "$CONTROL_FIRST_MIGRATION" ] && [ "$FLASK_DEBUG" = 'True' ]; then
    echo "Initial db";
    echo date > $CONTROL_FIRST_MIGRATION;
    flask db upgrade
fi

# Check current migration. This is important when we apply new version of app and usage Job object in kubernetes.
# We must wain before we run our new version of app, K8S object Job must be completed by applying all migrations.
if [ "$CHECK_MIGRATION" = 'True' ]; then
    counter=0
    until flask check_migration; do
      >&2 echo "Waiting for migrations (sleeping)..."
      sleep 1
      if [ $counter -gt "60" ]; then
        echo "Migrations wasn't applied. Exiting."
        exit 1
      fi
      counter=$(expr $counter + 1)
    done

    >&2 echo 'All migrations was applied - continuing...'
fi


case "$cmd" in
    migrate)
        flask db upgrade
    ;;
    test)
        flask test
    ;;
    cov)
        coverage run --source=. -m unittest discover 2> /dev/null && coverage report
    ;;
    *)
        $cmd  # usage start.sh or gunicorn.sh
    ;;
esac
