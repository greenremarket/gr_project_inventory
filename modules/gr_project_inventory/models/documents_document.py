# -*- coding: utf-8 -*-
"""
documents.document extension for Green Remarket.

Restores behaviour previously in grm_documents_project:
- search_panel_select_range : filtre le panneau gauche Documents sur le dossier
  de la tâche courante (evite d'avoir a passer par "Espace de travail > Tous").
- write() : génère un access_token sur l'attachment quand le tag Livrable est posé
  (nécessaire pour que les URLs de téléchargement portail fonctionnent).
- is_delivrable() : détecte si le document porte le tag Livrable.

⚠️ XML ref mise à jour : gr_project_inventory.documents_project_delivrable
   (et non plus grm_documents_project.documents_project_delivrable, module uninstallé).
"""

from collections import OrderedDict
from odoo import models, api


class DocumentsDocument(models.Model):
    _inherit = 'documents.document'

    @api.model
    def search_panel_select_range(self, field_name, **kwargs):
        """Restreint le panneau gauche au dossier de la tâche active.

        Quand on ouvre les Documents depuis une tâche (bouton smart), le contexte
        contient active_model='project.task' et active_id=<task_id>. Sans cette
        surcharge, le panneau gauche affiche toute l'arborescence et l'utilisateur
        doit naviguer manuellement vers "Espace de travail > Tous".
        """
        panel_select_range = super().search_panel_select_range(field_name, **kwargs)
        res_model = self._context.get('active_model')
        if res_model != 'project.task':
            return panel_select_range

        res_id = self._context.get('active_id')
        active_record = self.env[res_model].browse(res_id)
        if not active_record.exists():
            return panel_select_range

        task = active_record
        folder_id = task.documents_folder_id.id if task.documents_folder_id else False
        if not folder_id:
            return panel_select_range

        document_read_group = self.env['documents.document']._read_group(
            kwargs.get('search_domain', []), [], ['folder_id:array_agg']
        )
        folder_ids = document_read_group[0][0] if document_read_group else []

        records = (
            self.env['documents.folder']
            .with_context(hierarchical_naming=False)
            .search_read(
                [
                    '|',
                    ('id', 'child_of', folder_id),
                    ('id', 'in', folder_ids or []),
                ],
                ['display_name', 'description', 'parent_folder_id', 'has_write_access'],
            )
        )
        available_folder_ids = {record['id'] for record in records}

        values_range = OrderedDict()
        for record in records:
            record_id = record['id']
            if (
                record['parent_folder_id']
                and record['parent_folder_id'][0] not in available_folder_ids
            ):
                record['parent_folder_id'] = False
            value = record['parent_folder_id']
            record['parent_folder_id'] = value and value[0]
            values_range[record_id] = record

        return {
            'parent_field': 'parent_folder_id',
            'values': list(values_range.values()),
        }

    def write(self, vals):
        result = super().write(vals)
        # Quand le tag Livrable est ajouté, génère l'access_token de l'attachment
        # pour que l'URL de téléchargement portail (?access_token=...) soit valide.
        if 'tag_ids' in vals:
            for doc in self:
                if doc.is_delivrable() and doc.attachment_id and not doc.attachment_id.sudo().access_token:
                    doc.attachment_id.sudo().generate_access_token()
        return result

    def is_delivrable(self):
        """Retourne True si le document porte le tag Livrable (PJ)."""
        try:
            delivrable_tag = self.env.ref('gr_project_inventory.documents_project_delivrable')
        except Exception:
            return False
        return delivrable_tag in self.tag_ids
