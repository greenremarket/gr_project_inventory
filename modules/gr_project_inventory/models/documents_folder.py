# -*- coding: utf-8 -*-
"""
documents.folder extension for Green Remarket.
Ajoute la relation inverse task_ids pour accéder aux tâches depuis un dossier.
"""

from odoo import models, fields


class DocumentsFolder(models.Model):
    _inherit = 'documents.folder'

    task_ids = fields.One2many('project.task', 'documents_folder_id', string='Tasks')
