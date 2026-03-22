from odoo.addons.sale_project.controllers.portal import (
    SaleProjectCustomerPortal as BaseProjectCustomerPortal,
)
from odoo import _
from odoo.http import request
from odoo.osv.expression import OR, AND


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
        return (
            [
                ("project_id.privacy_visibility", "=", "portal"),
                ("active", "=", True),
                "|",
                (
                    "project_id.message_partner_ids",
                    "child_of",
                    [request.env.user.partner_id.id],
                ),
                (
                    "message_partner_ids",
                    "child_of",
                    [request.env.user.partner_id.id],
                ),
                ("tag_ids.name", "like", "PD3E"),
                ("message_partner_ids.task_portal_ok", "=", True),
            ]
            if request.env.user.partner_id.task_portal_ok
            else [(0, "=", 1)]
        )
