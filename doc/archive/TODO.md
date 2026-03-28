# Liste des tâches à faire

## Corrections de bugs
- [ ] Bug client dans le formulaire
- [ ] La date de l'élément dans l'inventaire lors de la duplication doit être `now()` au lieu de copier la date de l'élément original

## Améliorations UI/UX
- [ ] Limiter la longueur du nom du lot
- [ ] Changer le logo pour utiliser celui en test qui a la bonne taille

## Modifications de dates
- [ ] Changer la date de début d'opération

## Notes
- Pour la duplication d'élément d'inventaire : remplacer la copie de date par `fields.Datetime.now()`
- Pour le logo : utiliser le fichier de test qui a les bonnes dimensions
- Pour le nom du lot : ajouter une contrainte de longueur maximale 