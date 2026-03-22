from odoo import http
from odoo.http import request
from odoo.addons.project.controllers.portal import ProjectCustomerPortal
import logging

_logger = logging.getLogger(__name__)


class DocumentsProjectPortal(ProjectCustomerPortal):
    """Override portal to add documents to task page context."""
    
    def _task_get_page_view_values(self, task, access_token, **kwargs):
        """Override to add documents to the context."""
        values = super()._task_get_page_view_values(task, access_token, **kwargs)
        
        # Add documents to context so template can access them
        # Use sudo() here in the controller where it's allowed
        task_documents = task.sudo().document_ids
        _logger.info(f"Adding {len(task_documents)} documents to task {task.id} portal context")
        values['task_documents'] = task_documents
        
        return values
