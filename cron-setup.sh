#!/bin/bash

CRON_ENTRY="0 0 * * * $PYTHON_INTERPRETER $MAIN_PY_PATH"

echo "$CRON_ENTRY" > /tmp/cronjob

crontab /tmp/cronjob

rm /tmp/cronjob

echo "Cron job set up successfully."