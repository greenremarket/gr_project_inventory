# Script de Sauvegarde Cloud des Backups Odoo

Ce script permet de sauvegarder automatiquement les backups quotidiens d'Odoo (base de données + filestore) sur le cloud en utilisant rclone.

## Prérequis

1. Installer rclone :
```bash
curl https://rclone.org/install.sh | sudo bash
```

2. Configurer rclone pour OneDrive :
```bash
# Lancer la configuration
rclone config

# Choisir "n" pour une nouvelle configuration
# Choisir "onedrive" comme type de stockage
# Suivre les instructions pour l'authentification avec votre compte OneDrive Green Remarket
# Nommer la configuration "onedrive" (ou le nom que vous préférez)
```

## Configuration

1. Modifiez les variables dans le script `backup_to_cloud.sh` :
   - `BACKUP_DIR` : Chemin du répertoire des backups Odoo (/opt/odoo/backup)
   - `ONEDRIVE_REMOTE` : Nom de la configuration rclone pour OneDrive
   - `ONEDRIVE_DIR` : Nom du répertoire de destination sur OneDrive
   - `LOG_FILE` : Chemin du fichier de log

2. Testez le script :
```bash
./backup_to_cloud.sh
```

## Planification avec Cron

Pour exécuter la sauvegarde tous les jours à 1h du matin (après le backup Odoo), ajoutez cette ligne à votre crontab :

```bash
0 1 * * * /opt/odoo/test_addons/gr_project_inventory/scripts/backup/backup_to_cloud.sh
```

Pour éditer le crontab :
```bash
crontab -e
```

## Fonctionnalités

- Sauvegarde des backups quotidiens (base de données + filestore)
- Conservation des anciennes versions pendant 30 jours
- Exclusion des fichiers temporaires
- Journalisation détaillée
- Vérification des prérequis
- Nettoyage automatique des anciennes sauvegardes
- Transfert sécurisé via HTTPS

## Monitoring

Les logs sont stockés dans `/var/log/odoo/backup_odoo_daily.log`

## Restauration

Pour restaurer un backup :
```bash
rclone copy onedrive:Odoo_Backups/specific_backup/ LOCAL_DIR/
```

## Sécurité

- Le script vérifie les prérequis avant d'exécuter la sauvegarde
- Les erreurs sont journalisées
- Les anciennes versions sont conservées en cas de problème
- Les transferts sont chiffrés via HTTPS
- L'authentification se fait via OAuth2 