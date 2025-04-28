# -*- coding: utf-8 -*-
import logging
import pymysql
from odoo import api, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class ErasureService(models.AbstractModel):
    _name = 'gr.erasure.service'
    _description = 'Live MySQL bridge to Aiken Workbench'

    _SQL = """
        SELECT u.ProductType, u.Manufacturer, u.Model,
               d.Size AS hd_size, d.Model AS hd_model,
               d.Serial AS hd_sn, d.TimeStamp AS ts,
               d.Data AS cert_blob
        FROM Lots l
        JOIN Units u ON u.LotID = l.LotID
        JOIN Units_Devices d ON d.UnitID = u.UnitID
        WHERE l.Number = %s
          AND d.Category = 'STORAGE'
          AND d.Refurbished = 0;
    """

    def _dsn(self):
        ICP = self.env['ir.config_parameter'].sudo()
        return dict(
            host=ICP.get_param('gr.workbench_host', 'workbench.lan'),
            port=int(ICP.get_param('gr.workbench_port', 3306)),
            user=ICP.get_param('gr.workbench_user', 'odoo'),
            password=ICP.get_param('gr.workbench_pwd', ''),
            database=ICP.get_param('gr.workbench_db', 'awbc_db'),
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor,
        )

    def fetch_for_lot(self, lot_no):
        try:
            conn = pymysql.connect(**self._dsn())
            with conn.cursor() as cur:
                cur.execute(self._SQL, (lot_no,))
                rows = cur.fetchall()
        except pymysql.err.OperationalError as err:
            _logger.error("MySQL unreachable: %s", err)
            raise UserError(_("Cannot reach Workbench database."))
        finally:
            try:
                conn.close()
            except Exception:
                pass

        if not rows:
            raise UserError(_("Lot %s not found in Workbench.") % lot_no)
        return rows
