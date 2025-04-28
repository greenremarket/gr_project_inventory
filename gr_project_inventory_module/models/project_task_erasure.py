# -*- coding: utf-8 -*-
from odoo import models

class ProjectTaskErasure(models.Model):
    _inherit = 'project.task'

    def action_generate_erasure_certificate(self):
        self.ensure_one()
        rows = self.env['gr.erasure.service'].fetch_for_lot(self.lot_name)
        return self.env.ref('gr_project_inventory.erasure_certificate_report')\
                   .report_action(self, data={'rows': rows})
