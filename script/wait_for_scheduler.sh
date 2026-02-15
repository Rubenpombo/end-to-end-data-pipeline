#!/bin/bash
# script/wait_for_scheduler.sh

echo "Waiting for Airflow Scheduler to be healthy..."
MAX_RETRIES=60 # 5 minutes
COUNT=0

while [ "$(docker inspect --format='{{.State.Health.Status}}' scheduler 2>/dev/null)" != "healthy" ]; do
    sleep 5
    echo -n "."
    COUNT=$((COUNT+1))
    if [ $COUNT -ge $MAX_RETRIES ]; then
        echo "Timeout waiting for scheduler."
        exit 1
    fi
done
echo "Scheduler is ready!"
