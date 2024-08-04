#!/bin/bash

# Vérifie l'existence du fichier à chiffrer
if [ -z "$1" ]; then
  echo "Erreur: Aucun fichier spécifié pour le chiffrement."
  exit 1
fi

SQL_BACKUP_FILE=$1

# Chiffrement du fichier SQL
gpg --batch --yes --passphrase "$ENCRYPTION_PASSWORD" -c "$SQL_BACKUP_FILE"
if [ $? -ne 0 ]; then
  echo "Erreur: Impossible de chiffrer le fichier $SQL_BACKUP_FILE."
  exit 1
fi

# Supprimer le fichier SQL original
rm "$SQL_BACKUP_FILE"
if [ $? -ne 0 ]; then
  echo "Erreur: Impossible de supprimer le fichier SQL original."
  exit 1
fi

echo "Le fichier $SQL_BACKUP_FILE a été chiffré et l'original supprimé avec succès."

# DECRYPTION
# gpg --batch --yes --passphrase "$ENCRYPTION_PASSWORD" -o dump.sql -d {TIMESTAMP}-dump.sql.gpg