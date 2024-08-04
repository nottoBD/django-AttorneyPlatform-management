#!/bin/bash


if [ ! -f /home/devid/django-AttorneyPlatform-management/.env ]; then
  echo "Erreur: Fichier /home/devid/django-AttorneyPlatform-management/.env introuvable."
  exit 1
fi

set -a
source /home/devid/django-AttorneyPlatform-management/.env
set +a

/home/devid/django-AttorneyPlatform-management/utils/backup/script_postgresql_dump.sh
if [ $? -ne 0 ]; then
  echo "Erreur: Échec de l'exécution de script_postgresql_dump.sh."
  exit 1
fi

ENCRYPTED_SQL_BACKUP_FILE="${BACKUP_DIR}/$(date +"%F")-dump.sql.gpg"
LOG_BACKUP_FILE="${BACKUP_DIR}/$(date +"%F")-warnings.log"

/home/devid/django-AttorneyPlatform-management/utils/backup/script_ftp_transfer.sh "$ENCRYPTED_SQL_BACKUP_FILE" "$LOG_BACKUP_FILE"
if [ $? -ne 0 ]; then
  echo "Erreur: Échec de l'exécution de script_ftp_transfer.sh."
  exit 1
fi

echo "Toutes les étapes ont été exécutées avec succès."
