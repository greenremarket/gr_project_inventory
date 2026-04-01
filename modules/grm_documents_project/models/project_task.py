import zipfile
import base64
from collections import defaultdict
from io import BytesIO


from odoo import models, fields, api, _


def zip_binary_objects(objects_dict):
    buffer = BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for ext, files in objects_dict.items():
            for file in files:
                zip_path = f"{ext}/{file['name']}"
                # Ensure data is bytes, not base64 string or boolean
                data = file["data"]
                # Odoo's ir.attachment.datas always returns base64-encoded BYTES
                # (not str) from the ORM. isinstance(data, str) misses this case.
                # Binary files (PDF, XLSX) were being written as raw base64 text.
                if isinstance(data, (str, bytes)):
                    data = base64.b64decode(data)
                elif isinstance(data, bool) or data is None:
                    continue  # Skip empty/False attachments
                zf.writestr(zip_path, data)
    return buffer.getvalue()


class ProjectTask(models.Model):
    _inherit = "project.task"

    documents_folder_id = fields.Many2one(related=False)
    
    # Override shared_document_ids to show ALL documents in portal
    shared_document_ids = fields.One2many(
        'documents.document', 
        compute='_compute_shared_document_ids',
        string='Shared Documents',
        help='Documents visible in the portal'
    )
    
    @api.depends('document_ids')
    def _compute_shared_document_ids(self):
        """Override to make all document_ids visible as shared_document_ids in portal."""
        for task in self:
            # Show ALL documents in portal, not just shared ones
            task.shared_document_ids = task.document_ids


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
            # Get binary data from doc.datas or attachment
            file_data = doc.datas
            if not file_data and doc.attachment_id:
                file_data = doc.attachment_id.datas
            
            # Only add documents with actual data
            if file_data:
                documents_to_zip[doc.task_id.name].append(
                    {"name": doc.name, "data": file_data}
                )

        if not documents_to_zip:
            return _("No delivrables found."), b""

        return (
            f"{'_'.join(self.sudo().mapped('project_id.name'))}_delivrables.zip",
            zip_binary_objects(documents_to_zip),
        )
