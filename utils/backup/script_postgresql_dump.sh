#!/bin/bash

# Vérifie l'existence du fichier .env
if [ ! -f /home/devid/django-AttorneyPlatform-management/.env ]; then
  echo "Erreur: Fichier /home/devid/django-AttorneyPlatform-management/.env introuvable."
  exit 1
fi

set -a
source /home/devid/django-AttorneyPlatform-management/.env
set +a

# Vérifie les variables d'environnement
if [[ -z "$BACKUP_DIR" || -z "$DB_NAME" || -z "$DB_USER" || -z "$DB_PASSWORD" || -z "$DB_HOST" || -z "$DB_PORT" ]]; then
  echo "Erreur: Les variables d'environnement ne correspondent pas toutes."
  exit 1
fi

# Variables
TIMESTAMP=$(date +"%F")
SQL_BACKUP_FILE="$BACKUP_DIR/$TIMESTAMP-dump.sql"
LOG_BACKUP_FILE="$BACKUP_DIR/$TIMESTAMP-warnings.log"
LOG_DIR="$PROJECT_ROOT/log"

# Créer le dossier backup, si inexistant
if [ ! -d "$BACKUP_DIR" ]; then
  mkdir -p "$BACKUP_DIR"
  sudo chown -R $USER:$USER "$BACKUP_DIR"
fi

# Vérifie de disposer des droits d'écriture
if [ ! -w "$BACKUP_DIR" ]; then
  echo "Erreur: Impossible d'écrire dans le dossier $BACKUP_DIR."
  exit 1
fi

# Dump postgreSQL
PGPASSWORD=$DB_PASS pg_dump -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME > "$SQL_BACKUP_FILE"
if [ $? -ne 0 ]; then
  echo "Erreur: Impossible de dump la base de données avec ces identifiants."
  exit 1
fi

# Vérifie existance du dossier racine
APP_DIR=$PROJECT_ROOT
if [ ! -d "$APP_DIR" ]; then
  echo "Erreur: Dossier racine $APP_DIR introuvable."
  exit 1
fi

# Vérifie existance du dossier log
if [ ! -d "$LOG_DIR" ]; then
  echo "Erreur: Dossier log $LOG_DIR n'existe pas."
  exit 1
fi

if [ ! -f "$LOG_DIR/$TIMESTAMP-warnings.log" ]; then
  echo "Erreur: Fichier de log $LOG_DIR/$TIMESTAMP-warnings.log introuvable."
  exit 1
fi

cp "$LOG_DIR/$TIMESTAMP-warnings.log" "$LOG_BACKUP_FILE"
if [ $? -ne 0 ]; then
  echo "Erreur: Impossible de copier le fichier de log."
  exit 1
fi

./script_encrypt_dump.sh "$SQL_BACKUP_FILE"

echo "Backup terminée avec succès."