from odoo.addons.sale_project.controllers.portal import (
    SaleProjectCustomerPortal as BaseProjectCustomerPortal,
)
from odoo import _
from odoo.http import request
from odoo.osv.expression import OR, AND
import logging

_logger = logging.getLogger(__name__)


BLACKLISTED_SEARCHBAR_INPUTS = {
    "all",
    "content",
    "project",
    "milestone",
    "ref",
    "users",
    "stage",
    "status",
    "priority",
    "sale_order",
    "invoice",
}
BLACKLISTED_SEARCHBAR_GROUPBY = {
    "project",
    "milestone",
    "ref",
    "users",
    "sale_order",
    "sale_line",
}


class ProjectCustomerPortal(BaseProjectCustomerPortal):
    def _prepare_tasks_values(
        self,
        page,
        date_begin,
        date_end,
        sortby,
        search,
        search_in,
        groupby="none",
        url="/my/tasks",
        domain=[],
        su=False,
        project=False,
    ):
        """Override to ensure that the project is removed."""
        domain = AND(
            [
                domain,
                self._get_domain(),
            ]
        )
        return super()._prepare_tasks_values(
            page,
            date_begin,
            date_end,
            sortby,
            search,
            search_in,
            groupby,
            url,
            domain,
            su,
        )

    def _display_project_groupby(self, project):
        """Override to ensure that the project groupby is not displayed."""
        return False

    def _task_get_page_view_values(self, task, access_token, **kwargs):
        """Override to add documents to the context for portal display."""
        values = super()._task_get_page_view_values(task, access_token, **kwargs)
        
        # Add documents to context so template can access them
        # Use sudo() here in the controller where it's allowed
        task_documents = task.sudo().document_ids
        _logger.info(f"Adding {len(task_documents)} documents to task {task.id} portal context")
        values['task_documents'] = task_documents
        
        return values

    def _task_get_searchbar_groupby(self, milestones_allowed, project=False):
        searchbar_groupby = super()._task_get_searchbar_groupby(
            milestones_allowed, False
        )
        __ = {
            key: searchbar_groupby.pop(key, None)
            for key in BLACKLISTED_SEARCHBAR_GROUPBY
        }
        return dict(
            sorted(searchbar_groupby.items(), key=lambda item: item[1]["order"])
        )

    def _task_get_searchbar_inputs(self, milestones_allowed, project=False):
        searchbar_inputs = super()._task_get_searchbar_inputs(milestones_allowed, False)
        __ = {
            key: searchbar_inputs.pop(key, None) for key in BLACKLISTED_SEARCHBAR_INPUTS
        }
        searchbar_inputs["name"] = {
            "input": "name",
            "label": _("Name"),
            "order": 0,
        }
        if "customer" in searchbar_inputs:
            searchbar_inputs["customer"]["label"] = _("Customer / Subcustomer")
        return dict(sorted(searchbar_inputs.items(), key=lambda item: item[1]["order"]))

    def _task_get_searchbar_sortings(self, milestones_allowed, project=False):
        return super()._task_get_searchbar_sortings(milestones_allowed, True)

    def portal_my_tasks(
        self,
        page=1,
        date_begin=None,
        date_end=None,
        sortby=None,
        filterby=None,
        search=None,
        search_in="content",
        groupby="none",
        **kw
    ):
        response = super().portal_my_tasks(
            page,
            date_begin,
            date_end,
            sortby,
            filterby,
            search,
            search_in,
            groupby,
            **kw
        )
        response.qcontext.pop("searchbar_filters", None)
        return response

    def _task_get_search_domain(self, search_in, search):
        search_domain = [super()._task_get_search_domain(search_in, search)]
        if search_in in ("name", "all"):
            search_domain.append([("name", "ilike", search)])
        if search_in in ("customer", "all"):
            search_domain.append([("partner_id.child_ids", "ilike", search)])
        return OR(search_domain)

    def _get_domain(self):
        """Return domain for portal tasks: assigned OR follower OR project follower."""
        commercial_partner_id = request.env.user.partner_id.commercial_partner_id.id
        return (
            [
                ("project_id.privacy_visibility", "=", "portal"),
                ("active", "=", True),
                "|", "|",
                # Branch 1: User follows the project
                (
                    "project_id.message_partner_ids",
                    "child_of",
                    [commercial_partner_id],
                ),
                # Branch 2: User follows the task
                (
                    "message_partner_ids",
                    "child_of",
                    [commercial_partner_id],
                ),
                # Branch 3: User is assigned to the task
                ("user_ids", "in", [request.env.user.id]),
                # Keep portal access flag requirement
                ("message_partner_ids.task_portal_ok", "=", True),
            ]
            if request.env.user.partner_id.task_portal_ok
            else [(0, "=", 1)]
        )
