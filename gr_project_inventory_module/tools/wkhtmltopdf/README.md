# Installation de wkhtmltopdf

## Pourquoi wkhtmltopdf ?

wkhtmltopdf est une dépendance essentielle pour la génération de PDF dans Odoo. Il est utilisé pour convertir les rapports HTML en documents PDF. La version spécifique fournie ici (0.12.6.1 avec qt patché) est la version recommandée pour Odoo 16.0.

## Installation

1. Copiez le fichier `wkhtmltox_0.12.6.1-3.jammy_amd64.deb` sur le serveur
2. Installez le package avec la commande :
   ```bash
   sudo dpkg -i wkhtmltox_0.12.6.1-3.jammy_amd64.deb
   ```
3. Créez un lien symbolique pour que Odoo puisse trouver l'exécutable :
   ```bash
   sudo ln -s /usr/local/bin/wkhtmltopdf /usr/bin/wkhtmltopdf
   ```

## Configuration dans Odoo

Assurez-vous que le chemin vers wkhtmltopdf est correctement configuré dans le fichier de configuration d'Odoo (`odoo.conf`) :

```ini
wkhtmltopdf = /usr/local/bin/wkhtmltopdf
```

## Vérification

Pour vérifier que l'installation est correcte :

```bash
wkhtmltopdf --version
```

Vous devriez voir :
```
wkhtmltopdf 0.12.6.1 (with patched qt)
```

## Dépannage

Si vous rencontrez des problèmes :

1. Vérifiez que le lien symbolique existe et pointe vers le bon emplacement
2. Vérifiez les permissions sur l'exécutable
3. Vérifiez que le chemin est correct dans la configuration d'Odoo
4. Consultez les logs d'Odoo pour plus de détails sur les erreurs

## Notes

- Cette version est spécifiquement pour Ubuntu/Debian (architecture amd64)
- La version avec qt patché est nécessaire pour éviter les problèmes de rendu
- Ne pas utiliser d'autres versions de wkhtmltopdf car elles peuvent causer des problèmes de compatibilité 