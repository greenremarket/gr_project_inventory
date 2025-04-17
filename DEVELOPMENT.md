# Correction du formulaire de lancement d'opération

## Problèmes identifiés

1. **Problème avec les champs clients** :
   - Actuellement, il existe deux champs libres "Client Destination" et "Client Destinataire"
   - Ces deux champs devraient être fusionnés en un seul champ libre
   - Ce champ unique devrait être visible sur le formulaire principal de tâche
   - Actuellement, le champ client sur le formulaire principal fait appel au modèle contact et reste vide

2. **Problème avec la date d'opération** :
   - Lorsqu'une date d'opération est sélectionnée, elle s'enregistre comme date de fin au lieu de date de début

## Plan d'action

1. **Analyse du code existant** :
   - Identifier les fichiers qui gèrent le formulaire de lancement d'opération
   - Analyser comment les champs clients sont actuellement définis
   - Comprendre comment les dates sont actuellement gérées

2. **Correction des champs clients** :
   - Fusionner les deux champs en un seul
   - S'assurer que ce champ est correctement lié au formulaire principal de tâche

3. **Correction de la date d'opération** :
   - Modifier le code pour que la date sélectionnée s'enregistre comme date de début

4. **Tests** :
   - Vérifier que les modifications fonctionnent correctement
   - S'assurer qu'aucune régression n'a été introduite

## Journal de développement

### [18/04/2025]
- Création de la branche `fix/operations-form-issues`
- Création du fichier de développement
- Début de l'analyse du code existant

### [19/04/2025]
- Analyse complète des problèmes avec les champs clients et la date d'opération
- Correction du problème de date d'opération : modification du champ `date_deadline` en `date_start` dans le formulaire de lancement d'opération
- À tester sur la base greenremarket_test après l'installation du module 