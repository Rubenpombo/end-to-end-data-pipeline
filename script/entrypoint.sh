#!/bin/bash
# script/entrypoint.sh
set -e

if [ -e "/opt/airflow/requirements-airflow.txt" ]; then
  $(command -v pip) install -r /opt/airflow/requirements-airflow.txt
fi

$(command -v airflow) db migrate

# Idempotent bootstrap: fails silently if the admin user already exists
airflow users create \
  --username admin \
  --firstname admin \
  --lastname admin \
  --role Admin \
  --email admin@example.com \
  --password admin || true

# Airflow 3.x renamed the webserver command to api-server
exec airflow api-server
