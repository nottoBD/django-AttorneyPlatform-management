#!/bin/bash

# Vérifie l'existence du fichier .env
if [ ! -f ../.env ]; then
  echo "Erreur: Fichier ../.env introuvable."
  exit 1
fi

set -a
source ../.env
set +a

# Vérifie les variables d'environnement
if [[ -z "$BACKUP_DIR" || -z "$DB_NAME" || -z "$DB_USER" || -z "$DB_PASSWORD" || -z "$DB_HOST" || -z "$DB_PORT" ]]; then
  echo "Erreur: Les variables d'environnement ne correspondent pas toutes."
  exit 1
fi

# Variables
TIMESTAMP=$(date +"%F")
BACKUP_FILE="$BACKUP_DIR/neok-backup-$TIMESTAMP.tar.gz"
SQL_BACKUP_FILE="$BACKUP_DIR/neok-backup-$TIMESTAMP.sql"
LOG_DIR="/home/devid/django-AttorneyPlatform-management/log"

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
APP_DIR="/home/devid/django-AttorneyPlatform-management"
if [ ! -d "$APP_DIR" ]; then
  echo "Erreur: Dossier racine $APP_DIR introuvable."
  exit 1
fi

# Vérifie existance du dossier log
if [ ! -d "$LOG_DIR" ]; then
  echo "Erreur: Dossier log $LOG_DIR n'existe pas."
  exit 1
fi

# Vérifie existance du back-up
if [ ! -f "$SQL_BACKUP_FILE" ]; then
  echo "Erreur: SQL backup $SQL_BACKUP_FILE n'existe pas."
  exit 1
fi

# Backup des fichiers et de la base de données
tar --exclude='.gitkeep' -czvf "$BACKUP_FILE" -C "$BACKUP_DIR" "$(basename $SQL_BACKUP_FILE)" -C "$LOG_DIR" .
if [ $? -ne 0 ]; then
  echo "Erreur: Impossible de créer l'archive tar."
  exit 1
fi

# retirer le dump .sql, ne garder que l'archive
rm "$SQL_BACKUP_FILE"
if [ $? -ne 0 ]; then
  echo "Erreur: Impossible de supprimer le dump au format sql."
  exit 1
fi

echo "Backup terminée avec succès."
