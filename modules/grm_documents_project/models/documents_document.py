from collections import OrderedDict
from odoo import models, api


class Document(models.Model):
    _inherit = "documents.document"

    @api.model
    def search_panel_select_range(self, field_name, **kwargs):
        """Override to ensure the search panel works with documents."""
        panel_select_range = super().search_panel_select_range(field_name, **kwargs)
        res_model = self._context.get("active_model")
        if res_model != "project.task":
            return panel_select_range

        res_id = self._context.get("active_id")
        active_record = self.env[res_model].browse(res_id)
        if not active_record.exists():
            return super().search_panel_select_range(field_name, **kwargs)
        task = active_record

        document_read_group = self.env["documents.document"]._read_group(
            kwargs.get("search_domain", []), [], ["folder_id:array_agg"]
        )
        folder_ids = document_read_group[0][0]
        records = (
            self.env["documents.folder"]
            .with_context(hierarchical_naming=False)
            .search_read(
                [
                    "|",
                    ("id", "child_of", task.documents_folder_id.id),
                    ("id", "in", folder_ids),
                ],
                ["display_name", "description", "parent_folder_id", "has_write_access"],
            )
        )
        available_folder_ids = set(record["id"] for record in records)

        values_range = OrderedDict()
        for record in records:
            record_id = record["id"]
            if (
                record["parent_folder_id"]
                and record["parent_folder_id"][0] not in available_folder_ids
            ):
                record["parent_folder_id"] = False
            value = record["parent_folder_id"]
            record["parent_folder_id"] = value and value[0]
            values_range[record_id] = record

        return {
            "parent_field": "parent_folder_id",
            "values": list(values_range.values()),
        }

    def write(self, vals):
        result = super().write(vals)
        # When the Delivrable tag is added, generate the attachment access token
        # so the portal download URL (?access_token=...) works for portal users.
        if 'tag_ids' in vals:
            for doc in self:
                if doc.is_delivrable() and doc.attachment_id and not doc.attachment_id.sudo().access_token:
                    doc.attachment_id.sudo().generate_access_token()
        return result

    def is_delivrable(self):
        """Check if the document is a delivrable."""
        delivrable_tag = self.env.ref("grm_documents_project.documents_project_delivrable")
        return delivrable_tag in self.tag_ids
