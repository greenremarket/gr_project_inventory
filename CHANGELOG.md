# Changelog

## [Version 1.2] - 2024-04-15

### Nouveautés
- Amélioration des rapports d'inventaire interne avec une meilleure mise en page et des fonctionnalités supplémentaires
- Optimisation du rapport de divergences pour une meilleure lisibilité
- Ajout de la gestion des états d'inventaire (NEW, REFURB, NEW-OPEN-BOX, TBD)
- Amélioration de la gestion des observations sur les articles

### Modifications
- Refonte du système de génération de PDF avec wkhtmltopdf
- Optimisation des performances des rapports
- Amélioration de la gestion des codes-barres
- Mise à jour des tests unitaires pour couvrir les nouvelles fonctionnalités

### Corrections
- Correction des problèmes de génération de PDF
- Amélioration de la gestion des erreurs dans les rapports
- Correction des problèmes de formatage dans les exports Excel
- Optimisation de la gestion de la mémoire dans les rapports volumineux

### Notes techniques
- Mise à jour des dépendances Python
- Amélioration de la documentation du code
- Optimisation des requêtes SQL dans les rapports
- Ajout de logs détaillés pour le débogage

## [Version 1.1] - 2024-03-14

### Fonctionnalités existantes
- Gestion des inventaires clients et internes
- Suivi des divergences entre inventaires
- Génération de rapports Excel
- Support des codes-barres
- Catégorisation des produits (fabricant, type, châssis) 