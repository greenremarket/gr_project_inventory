from odoo import http
from odoo.http import request, content_disposition
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.exceptions import AccessError, MissingError
from werkzeug.exceptions import Forbidden


def _get_zip_headers(content, filename):
    return [
        ("Content-Type", "application/zip"),
        ("X-Content-Type-Options", "nosniff"),
        ("Content-Length", len(content)),
        ("Content-Disposition", content_disposition(filename)),
    ]


class DelivrablesController(CustomerPortal):
    @http.route(
        ["/delivrable/download"],
        type="http",
        auth="public",
        methods=["POST"],
        website=True,
        csrf=False,  # Disable CSRF for portal access
    )
    def download(self, task_ids, access_token=None, **kwargs):
        """
        Endpoint to download delivrables.
        Supports both logged-in users (internal/portal) and portal users with access_token.
        :param task_ids: Comma-separated list of task IDs to download delivrables for.
        :param access_token: Optional access token for portal users without session.
        :return: ZIP file response.
        """
        if not task_ids:
            return http.Response("No tasks provided.", status=400, headers={"Content-Type": "text/plain"})
        
        try:
            task_id_list = list(map(int, task_ids.split(",")))
        except ValueError:
            return http.Response("Invalid task IDs.", status=400, headers={"Content-Type": "text/plain"})
        
        # Check if user is logged in
        is_logged_in = not request.env.user._is_public()
        
        # Validate access for each task
        validated_tasks = request.env['project.task']
        
        for task_id in task_id_list:
            try:
                if is_logged_in:
                    # User is logged in (internal or portal user with session)
                    # Use normal access rights checking
                    task = request.env['project.task'].browse(task_id)
                    task.check_access_rights('read')
                    task.check_access_rule('read')
                    validated_tasks |= task.sudo()
                else:
                    # Public user with access_token
                    # Use CustomerPortal's access validation method
                    task_sudo = self._document_check_access('project.task', task_id, access_token=access_token)
                    validated_tasks |= task_sudo
            except (AccessError, MissingError, Forbidden):
                # Skip tasks user doesn't have access to
                continue
        
        if not validated_tasks:
            return http.Response("No accessible tasks found.", status=403, headers={"Content-Type": "text/plain"})
        
        # Generate ZIP file - validated_tasks is already in sudo mode
        filename, zip_object = validated_tasks.zip_delivrable_documents()
        
        if not zip_object:
            return http.Response(filename or "No deliverables found.", status=404, headers={"Content-Type": "text/plain"})
        
        headers = _get_zip_headers(zip_object, filename)
        return request.make_response(zip_object, headers)
