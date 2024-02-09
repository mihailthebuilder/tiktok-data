#!/bin/bash

export $(cat .env | grep -v '#' | xargs)

scp -r "$CHROME_PROFILE_DIR" "root@$SERVER_IP":"/root/cron"