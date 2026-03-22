import zipfile
from collections import defaultdict
from io import BytesIO


from odoo import models, fields, _


def zip_binary_objects(objects_dict):
    buffer = BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for ext, files in objects_dict.items():
            for file in files:
                zip_path = f"{ext}/{file['name']}"
                zf.writestr(zip_path, file["data"])
    return buffer.getvalue()


class ProjectTask(models.Model):
    _inherit = "project.task"

    documents_folder_id = fields.Many2one(related=False)

    def action_view_documents_project_task(self):
        action = super().action_view_documents_project_task()
        if not self.documents_folder_id:
            self._init_documents_folder()
        return action

    def _get_document_folder(self):
        # OVERRIDE to ensure the documents folder is initialized
        return self.documents_folder_id or self._init_documents_folder()

    def _init_documents_folder(self):
        """Initialize the documents folder for the task."""
        documents_folder = self.env["documents.folder"].create(
            self._prepare_documents_folder()
        )
        self.documents_folder_id = documents_folder.id
        return documents_folder

    def _prepare_documents_folder(self):
        """Compute folder'values to create for the task."""
        return {
            "name": self.name,
            "parent_folder_id": self.project_id.documents_folder_id.id,
            "task_ids": [fields.Command.link(self.id)],
        }

    def zip_delivrable_documents(self):
        documents = (
            self.sudo().mapped("document_ids").filtered(lambda doc: doc.is_delivrable())
        )
        documents_to_zip = defaultdict(list)
        for doc in documents:
            documents_to_zip[doc.task_id.name].append(
                {"name": doc.name, "data": doc.raw}
            )

        if not documents_to_zip:
            return _("No delivrables found."), b""

        return (
            f"{'_'.join(self.sudo().mapped('project_id.name'))}_delivrables.zip",
            zip_binary_objects(documents_to_zip),
        )
