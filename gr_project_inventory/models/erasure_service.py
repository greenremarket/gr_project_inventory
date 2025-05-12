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
        SELECT
            u.UnitID,
            u.AssetTag,
            u.SerialNumber,
            u.Model,
            u.ProductType,
            u.Manufacturer,
            u.Audited,
            d.Didx AS hd_idx,
            d.Model AS hd_model,
            d.Serial AS hd_sn,
            d.Size AS hd_size,
            d.Erased AS erased_flag
        FROM Lots l
        JOIN Units u ON u.LotID = l.LotID
        JOIN Units_Devices d ON d.UnitID = u.UnitID
        WHERE l.Number = %s
          AND d.Category = 'STORAGE'
          AND d.Refurbished = 0
        ORDER BY u.UnitID, d.Didx
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
        """
        Fetches erasure data for a given lot from the Aiken Workbench.
        Returns a list of dicts ready for the report, with all required fields and error handling.
        """
        try:
            conn = pymysql.connect(**self._dsn())
            with conn.cursor() as cur:
                cur.execute(self._SQL, (lot_no,))
                raw_rows = cur.fetchall()
        except pymysql.err.OperationalError as err:
            _logger.error("MySQL unreachable: %s", err)
            raise UserError(_("Cannot reach Workbench database."))
        except Exception as e:
            _logger.error("Unexpected error fetching erasure data: %s", str(e), exc_info=True)
            raise UserError(_("Unexpected error fetching erasure data: %s") % str(e))
        finally:
            try:
                conn.close()
            except Exception:
                pass

        if not raw_rows:
            raise UserError(_("Lot %s not found in Workbench.") % lot_no)

        rows = []
        for r in raw_rows:
            try:
                # Build Host Machine string robustly
                asset_tag = r.get('AssetTag') or ''
                serial_number = r.get('SerialNumber') or ''
                model = r.get('Model') or ''
                host_parts = []
                if asset_tag.strip():
                    host_parts.append(asset_tag.strip())
                if serial_number.strip():
                    host_parts.append(serial_number.strip())
                host_machine = ', '.join(host_parts)
                if model.strip():
                    host_machine = f"{host_machine} - {model.strip()}" if host_machine else model.strip()
                # Method: Erased flag (1 = 'Zeros', 0 = 'Unknown')
                method = 'Zeros' if r.get('erased_flag', 0) else 'Unknown'
                # Compose row for report
                rows.append({
                    'host_machine': host_machine,
                    'hd_idx': r.get('hd_idx', '-'),
                    'hd_model': r.get('hd_model', '-'),
                    'hd_sn': r.get('hd_sn', '-'),
                    'hd_size': r.get('hd_size', '-'),
                    'erasure_id': r.get('UnitID', '-'),
                    'method': method,
                    'timestamp': str(r.get('Audited', '-')),
                })
            except Exception as e:
                _logger.error("Error formatting row for report: %s", str(e), exc_info=True)
                continue

        if not rows:
            raise UserError(_("No erasure records found for lot %s.") % lot_no)
        return rows
