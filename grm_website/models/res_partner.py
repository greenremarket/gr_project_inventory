from odoo import models, fields


class ResPartner(models.Model):
    _inherit = "res.partner"

    task_portal_ok = fields.Boolean(
        string="Task Portal Access",
        help="Allow this partner to access the task portal.",
    )
