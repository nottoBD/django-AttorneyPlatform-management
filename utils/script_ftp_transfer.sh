#!/bin/bash

set -a
source /opt/neok-budget/.env
set +a

if [[ -z "$FTP_USER" || -z "$FTP_PASSWORD" || -z "$FTP_SERVER" || -z "$BACKUP_DIR" || -z "$REMOTE_BACKUP_DIR" ]]; then
  echo "Erreur: Vérifiez les variables d'environnements."
  exit 1
fi

lftp -u "$FTP_USER","$FTP_PASSWORD" "$FTP_SERVER" <<EOF
mirror -R "$BACKUP_DIR" "$REMOTE_BACKUP_DIR"
bye
EOF

if [[ $? -ne 0 ]]; then
  echo "Erreur: Les fichiers n'ont pas été transferés."
  exit 1
else
  echo "Success: Les fichiers ont été transferés!."
fi
