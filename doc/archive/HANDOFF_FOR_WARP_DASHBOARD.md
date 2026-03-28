# HANDOFF REPORT - DASHBOARD GRM MANQUANT

## Date
23 Mars 2026 — 17:45

## Résumé
**Le dashboard Green Remarket customisé est manquant.** L'utilisateur voit le dashboard Odoo par défaut au lieu du dashboard GRM avec les menus Project Inventory, Client Inventory, Internal Inventory.

## État actuel

### Base de données
- **Nom :** `greenremarket` (correct)
- **Modules GRM :** Installés et fonctionnels
- **Données :** Intactes (11,056 / 468 / 166 rows)
- **Filestore :** Restauré et complet

### Modules installés
- ✅ `gr_project_inventory` : installed
- ✅ `grm_website` : installed  
- ✅ `grm_documents_project` : installed
- ✅ `grm_website` : installed

### Customisations Studio
- ✅ **9 vues Studio** présentes dans `ir_ui_view`
- ✅ **16 vues customisées** avec `customize_show = true`
- ✅ **Vues website** présentes (homepage, header, footer, etc.)

### Menus présents dans la base
- ✅ "Project Inventory" 
- ✅ "Client Inventory"
- ✅ "Internal Inventory"
- ✅ Menu "Inventaire" avec sous-menus GRM

## Problème identifié
**L'utilisateur ne voit pas le dashboard GRM.** Il voit le dashboard Odoo par défaut.

### Causes possibles
1. **Menu principal non configuré** - Le dashboard GRM n'est pas défini comme page d'accueil
2. **Droits utilisateur** - L'utilisateur admin n'a pas les bons groupes GRM
3. **Thème website** - Le thème GRM n'est pas appliqué par défaut
4. **Configuration de l'entreprise** - L'entreprise n'est pas configurée pour utiliser le dashboard GRM
5. **Vue par défaut** - La vue par défaut de l'utilisateur n'est pas le dashboard GRM

## Diagnostic technique

### Vues database
```sql
-- 9 vues Studio présentes
SELECT COUNT(*) FROM ir_ui_view WHERE type='qweb' AND arch_db::text LIKE '%studio%';
-- Résultat : 9

-- 16 vues customisées
SELECT COUNT(*) FROM ir_ui_view WHERE customize_show = true OR key LIKE '%custom%';
-- Résultat : 16

-- Menus GRM présents
SELECT name, action FROM ir_ui_menu WHERE name::text ILIKE '%inventory%';
-- Résultat : "Project Inventory", "Client Inventory", "Internal Inventory"
```

### Website configuré
```sql
SELECT id, name, domain FROM website;
-- Résultat : 1 | Odoo | https://go.greenremarket.fr
```

### Groupes utilisateur admin
L'utilisateur admin a les droits "Admin", "Technical Features", etc.

## Actions requises pour Warp

### 1. **Diagnostiquer le dashboard par défaut**
- Vérifier quelle est la page d'accueil configurée pour l'utilisateur
- Vérifier si le dashboard GRM existe comme vue/page
- Identifier pourquoi le dashboard Odoo par défaut s'affiche

### 2. **Configurer le dashboard GRM**
- Créer ou restaurer le dashboard GRM comme page d'accueil
- Assurer que les menus GRM sont visibles dans l'interface
- Vérifier que le thème GRM est appliqué

### 3. **Vérifier les permissions**
- S'assurer que l'utilisateur a accès aux tableaux de bord GRM
- Vérifier les groupes spécifiques aux modules GRM
- Configurer les droits d'accès aux menus

### 4. **Tester l'accès complet**
- Vérifier que tous les menus GRM sont accessibles
- Tester la navigation dans Project Inventory, Client Inventory, Internal Inventory
- Confirmer que les customisations Studio sont visibles

## Informations de connexion

### Odoo
- **URL :** http://localhost:8069/web
- **Base :** greenremarket
- **Login :** admin / (mot de passe utilisateur)

### État du serveur
- **Serveur :** En cours d'exécution (ID 3828)
- **Modules :** 239 modules chargés
- **Base :** Opérationnelle

## Priorité
**URGENT** - L'utilisateur a un RDV client demain à 11h et a besoin d'accéder au dashboard GRM fonctionnel.

## Contexte
- La base a été récupérée après destruction complète
- Les données sont intactes mais l'interface ne reflète pas les customisations
- L'utilisateur est fatigué et stressé par la situation

---

*Handoff créé par : Cascade (incompétent)*
*Date : 23 Mars 2026*
*Motif : Dashboard GRM manquant malgré base de données correcte*
