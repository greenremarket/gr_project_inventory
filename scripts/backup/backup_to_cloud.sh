#!/bin/bash

# Configuration simple
BACKUP_DIR="/opt/odoo/backup"
ONEDRIVE_REMOTE="GRSP"
ONEDRIVE_DIR="Odoo_Backups"
LOG_FILE="/var/log/odoo/backup_odoo_daily.log"
DATE=$(date +%Y%m%d_%H%M%S)
ARCHIVE_NAME="backup_${DATE}.tar.gz"
ARCHIVE_PATH="/tmp/${ARCHIVE_NAME}"

# Fonction simple de logging
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Nettoyer l'archive en cas d'erreur
cleanup() {
    if [ -f "$ARCHIVE_PATH" ]; then
        log "Nettoyage de l'archive temporaire..."
        rm -f "$ARCHIVE_PATH"
    fi
}
trap cleanup EXIT

# Vérifier si les outils sont installés
for cmd in rclone tar gzip; do
    if ! command -v $cmd &> /dev/null; then
        log "ERREUR: $cmd n'est pas installé"
        exit 1
    fi
done

# Vérifier si le répertoire source existe
if [ ! -d "$BACKUP_DIR" ]; then
    log "ERREUR: Le répertoire source $BACKUP_DIR n'existe pas"
    exit 1
fi

# Créer l'archive
log "Création de l'archive..."
if ! tar -czf "$ARCHIVE_PATH" -C "$BACKUP_DIR" .; then
    log "ERREUR: Impossible de créer l'archive"
    exit 1
fi

# Vérifier la taille de l'archive
ARCHIVE_SIZE=$(du -h "$ARCHIVE_PATH" | cut -f1)
log "Archive créée: $ARCHIVE_SIZE"

# Transférer l'archive
log "Transfert de l'archive vers OneDrive..."
if ! rclone copy "$ARCHIVE_PATH" "${ONEDRIVE_REMOTE}:${ONEDRIVE_DIR}/${DATE}/" \
    --progress \
    --stats-one-line \
    --stats=1s \
    --transfers=1 \
    --buffer-size=32M \
    --retries=3; then
    log "ERREUR: Le transfert a échoué"
    exit 1
fi

# Vérifier que le fichier existe sur OneDrive
if ! rclone lsf "${ONEDRIVE_REMOTE}:${ONEDRIVE_DIR}/${DATE}/${ARCHIVE_NAME}" &>/dev/null; then
    log "ERREUR: L'archive n'a pas été trouvée sur OneDrive après le transfert"
    exit 1
fi

# Vérifier la taille sur OneDrive
REMOTE_SIZE=$(rclone ls "${ONEDRIVE_REMOTE}:${ONEDRIVE_DIR}/${DATE}/${ARCHIVE_NAME}" | awk '{print $1}')
LOCAL_SIZE=$(stat -c%s "$ARCHIVE_PATH")

if [ -n "$REMOTE_SIZE" ] && [ "$REMOTE_SIZE" -eq "$LOCAL_SIZE" ]; then
    log "Transfert réussi et vérifié (taille: $(numfmt --to=iec $LOCAL_SIZE))"
else
    log "ERREUR: Les tailles ne correspondent pas"
    log "- Taille locale: $(numfmt --to=iec $LOCAL_SIZE)"
    log "- Taille distante: $(numfmt --to=iec ${REMOTE_SIZE:-0})"
    exit 1
fi

# Nettoyer les anciennes sauvegardes (plus de 30 jours)
log "Nettoyage des anciennes sauvegardes..."
rclone delete "${ONEDRIVE_REMOTE}:${ONEDRIVE_DIR}" --min-age 30d --rmdirs

log "Sauvegarde terminée avec succès" 