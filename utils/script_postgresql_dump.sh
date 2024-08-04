#!/bin/bash

set -a
source /opt/neok-budget/.env
set +a

TIMESTAMP=$(date +"%F")
BACKUP_FILE="$BACKUP_DIR/neok-backup-$TIMESTAMP.tar.gz"

mkdir -p $BACKUP_DIR

PGPASSWORD=$DB_PASS pg_dump -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME > $SQL_BACKUP_FILE

tar -czvf $BACKUP_FILE /opt/neok-budget $SQL_BACKUP_FILE

rm $SQL_BACKUP_FILE
