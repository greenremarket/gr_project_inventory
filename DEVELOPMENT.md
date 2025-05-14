# Greenremarket - Guide de développement

## AVERTISSEMENTS IMPORTANTS - ENVIRONNEMENT DE PRODUCTION

⚠️ **NE JAMAIS** toucher aux éléments suivants en environnement de production :

- Base de données `greenremarket` (utiliser uniquement `greenremarket_test` pour les tests)
- Répertoire `/opt/odoo/extra_addons/` (utiliser uniquement `/opt/odoo/test_addons/`)
- Service Odoo principal (seulement `odoo-test`)

## Environnement de test

### Mettre à jour un module sur le serveur de test

Pour mettre à jour un module sur le serveur de test, utilisez la commande suivante :

```bash
python3 /opt/odoo/odoo-bin -d greenremarket_test --stop-after-init -u gr_project_inventory --addons-path=/opt/odoo/addons,/opt/odoo/enterprise,/opt/odoo/oca_addons,/opt/odoo/test_addons/greenremarket,/opt/odoo/test_addons && sudo systemctl restart odoo-test
```

Cette commande :
1. Met à jour le module spécifié (ici `gr_project_inventory`) dans la base de test
2. Redémarre le service Odoo de test pour prendre en compte les modifications

> **IMPORTANT**: Ne jamais utiliser la base de données `greenremarket` pour les tests, c'est la base de production.
