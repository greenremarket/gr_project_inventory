#!/bin/bash
# proxmox_disk_alert.sh — Alerte espace disque LVM Proxmox
# Cron : 5 * * * * /usr/local/bin/proxmox_disk_alert.sh  (5 min apres chaque heure, evite collision logrotate/dpkg a 00:00)
#
# v2 — fixes:
#   1. Retry lvs jusqu'a 3 fois avant d'alerter (evite les faux positifs
#      quand LVM est verrouille par un snapshot en cours)
#   2. Surveille le thin pool data% (le vrai indicateur) au lieu de
#      vg_free qui est structurellement bas sur un setup thin-provisioned

ALERT_EMAIL="morad@greenremarket.fr"
THIN_POOL="pve/data"   # VG/nom du thin pool Proxmox
THRESHOLD_PCT=80       # Alerte si thin pool utilise > 80%
HOSTNAME=$(hostname)
MAX_RETRIES=6
RETRY_DELAY=15  # secondes entre chaque essai (total 90s max)

# --- Lecture du thin pool data% avec retry ---
DATA_PCT=""
for i in $(seq 1 $MAX_RETRIES); do
    DATA_PCT=$(lvs --noheadings -o data_percent "$THIN_POOL" 2>/dev/null | awk '{printf "%d", $1}')
    if [ -n "$DATA_PCT" ]; then
        break
    fi
    sleep $RETRY_DELAY
done

if [ -z "$DATA_PCT" ]; then
    # lvs a echoue meme apres retries -> vrai probleme LVM a investiguer
    echo "Impossible de lire l'utilisation du thin pool $THIN_POOL apres $MAX_RETRIES essais (LVM locked?)." \
        | mail -s "[ALERTE Proxmox] Erreur lecture LVM thin pool" "$ALERT_EMAIL"
    echo "$(date -Iseconds) ERREUR: lvs thin pool illisible apres $MAX_RETRIES retries" >> /var/log/proxmox_disk_alert.log
    exit 1
fi

if [ "$DATA_PCT" -ge "$THRESHOLD_PCT" ]; then
    DETAIL=$(lvs --noheadings -o lv_name,lv_size,data_percent,pool_lv 2>/dev/null)
    CT_LIST=$(pct list 2>/dev/null)
    SNAP_LIST=$(for id in $(pct list 2>/dev/null | awk 'NR>1{print $1}'); do echo "CT$id:"; pct listsnapshot "$id" 2>/dev/null; done)

    BODY="ALERTE THIN POOL PROXMOX
Hote : $HOSTNAME
Thin pool $THIN_POOL utilise a ${DATA_PCT}% (seuil : ${THRESHOLD_PCT}%)

Detail LVs :
$DETAIL

Snapshots existants :
$SNAP_LIST

Containers actifs :
$CT_LIST

Actions possibles :
1. Supprimer des anciens snapshots : pct delsnapshot <VMID> <snapname>
2. Supprimer des CT inutilises : pct stop <VMID> && pct destroy <VMID>"

    echo "$BODY" | mail -s "[ALERTE Proxmox] Thin pool critique : ${DATA_PCT}% utilise" "$ALERT_EMAIL"
    echo "$(date -Iseconds) ALERTE: thin pool ${DATA_PCT}% — mail envoye" >> /var/log/proxmox_disk_alert.log
else
    echo "$(date -Iseconds) OK: thin pool ${DATA_PCT}% utilise (seuil ${THRESHOLD_PCT}%)" >> /var/log/proxmox_disk_alert.log
fi
