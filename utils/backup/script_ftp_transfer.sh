#!/bin/bash

# Vérifie l'existence des fichiers à transférer
if [ -z "$1" ] || [ -z "$2" ]; then
  echo "Erreur: Deux fichiers sont nécessaires pour le transfert."
  exit 1
fi

ENCRYPTED_SQL_BACKUP_FILE=$1
LOG_BACKUP_FILE=$2

if [[ -z "$FTP_USER" || -z "$FTP_PASSWORD" || -z "$FTP_SERVER" || -z "$REMOTE_DUMP_DIR" || -z "$REMOTE_LOG_DIR" ]]; then
  echo "Erreur: Les variables d'environnement FTP ne correspondent pas toutes."
  exit 1
fi

# Si FTP_PORT n'est pas défini, utiliser une valeur par défaut
FTP_PORT=${FTP_PORT:-21}

# Envoyer le fichier SQL chiffré au serveur FTP
lftp -u "$FTP_USER","$FTP_PASSWORD" -e "set ssl:verify-certificate no; put -O \"$REMOTE_DUMP_DIR\" \"$ENCRYPTED_SQL_BACKUP_FILE\"; bye" "$FTP_SERVER" -p "$FTP_PORT"
if [ $? -ne 0 ]; then
  echo "Erreur: Le fichier SQL chiffré n'a pas été transféré."
  exit 1
fi

# Envoyer le fichier de log au serveur FTP
lftp -u "$FTP_USER","$FTP_PASSWORD" -e "set ssl:verify-certificate no; put -O \"$REMOTE_LOG_DIR\" \"$LOG_BACKUP_FILE\"; bye" "$FTP_SERVER" -p "$FTP_PORT"
if [ $? -ne 0 ]; then
  echo "Erreur: Le fichier de log n'a pas été transféré."
  exit 1
fi

# Supprimer les fichiers locaux après le transfert
rm "$ENCRYPTED_SQL_BACKUP_FILE"
if [ $? -ne 0 ]; then
  echo "Erreur: Impossible de supprimer le fichier SQL chiffré local."
  exit 1
fi

rm "$LOG_BACKUP_FILE"
if [ $? -ne 0 ]; then
  echo "Erreur: Impossible de supprimer le fichier de log local."
  exit 1
fi

echo "Les fichiers ont été transférés et supprimés localement avec succès."
