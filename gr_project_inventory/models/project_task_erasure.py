# -*- coding: utf-8 -*-
from odoo import models

class ProjectTaskErasure(models.Model):
    _inherit = 'project.task'

    def action_generate_erasure_certificate(self):
        self.ensure_one()
        import logging
        from odoo.exceptions import UserError
        logger = logging.getLogger(__name__)

        if not self.lot_name:
            logger.warning('No lot_name set for project.task ID %s', self.id)
            raise UserError('No Lot Name is set for this task. Cannot generate erasure certificate.')

        try:
            rows = self.env['gr.erasure.service'].fetch_for_lot(self.lot_name)
        except Exception as e:
            logger.error('Error fetching erasure rows for lot %s: %s', self.lot_name, str(e), exc_info=True)
            raise UserError('Could not connect to Aiken or fetch erasure data. Please contact your administrator.')

        if not rows:
            logger.info('No erasure data found for lot %s (task ID %s)', self.lot_name, self.id)
            raise UserError('No erasure data found for this lot in Aiken. Please check the lot name or try again later.')

        logger.info('Erasure rows for lot %s (task ID %s): %r', self.lot_name, self.id, rows)
        return self.env.ref('gr_project_inventory.erasure_certificate_report').report_action(self, data={'rows': rows, 'lot_name': self.lot_name})
