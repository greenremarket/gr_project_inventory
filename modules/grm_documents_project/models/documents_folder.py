from odoo import fields, models


class DocumentFolder(models.Model):
    _inherit = "documents.folder"

    task_ids = fields.One2many("project.task", "documents_folder_id")
