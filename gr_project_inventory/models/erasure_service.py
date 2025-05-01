# -*- coding: utf-8 -*-
import logging
import pymysql
import os
from odoo import api, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class ErasureService(models.AbstractModel):
    _name = 'gr.erasure.service'
    _description = 'Live MySQL bridge to Aiken Workbench'

    _SQL = """
        SELECT u.ProductType, u.Manufacturer, u.Model,
               d.Size AS hd_size, d.Model AS hd_model,
               d.Serial AS hd_sn,
               d.Data AS cert_blob  # No timestamp column in Units_Devices
        FROM Lots l
        JOIN Units u ON u.LotID = l.LotID
        JOIN Units_Devices d ON d.UnitID = u.UnitID
        WHERE l.Number = %s
          AND d.Category = 'STORAGE'
          AND d.Refurbished = 0;
    """

    def _dsn(self):
        # First, try to read credentials from standard MySQL environment variables
        # See /opt/odoo/MYSQL_WORKBENCH_README.md for details
        host = os.environ.get('MYSQL_HOST')
        port = os.environ.get('MYSQL_PORT')
        user = os.environ.get('MYSQL_USER')
        password = os.environ.get('MYSQL_PASSWORD')
        database = os.environ.get('MYSQL_DATABASE')

        # If any are missing, fall back to Odoo config parameters
        ICP = self.env['ir.config_parameter'].sudo()
        host = host or ICP.get_param('gr.workbench_host', 'workbench.lan')
        port = int(port or ICP.get_param('gr.workbench_port', 3306))
        user = user or ICP.get_param('gr.workbench_user', 'odoo')
        password = password or ICP.get_param('gr.workbench_pwd', '')
        database = database or ICP.get_param('gr.workbench_db', 'awbc_db')

        # Add comments to clarify the logic
        # If you want to enforce that all env vars must be set, raise an error here
        # For now, fallback to config parameters as above

        return dict(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
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
