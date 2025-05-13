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

    _AUDIT_SQL = """
        SELECT
            u.UnitID,
            l.Number AS LotID,
            u.AssetTag,
            u.Created,
            u.ProductType,
            u.Manufacturer AS Manufacturer,
            u.Model,
            u.Chassis,
            u.PartNumber,
            u.SerialNumber,
            d1.Size AS DisplaySize,
            CONCAT(d1.Info1, ' x ', d1.Info2) AS Resolution,
            d2.Model AS Processor,
            d2.Speed AS ProcSpeed,
            d2.Info1 AS ProcGen,
            MAX(CASE WHEN d3.Category = 'RAM' THEN d3.Size ELSE NULL END) AS RAM,
            d4.Size AS Storage1Size,
            d4.Info1 AS Storage1Type,
            d4.Model AS Storage1Model,
            d4.Serial AS Storage1Serial,
            d5.Model AS Optical,
            d6.Model AS Keyb,
            d7.Model AS Webcam,
            d8.Model AS Videocard,

            COALESCE(u.OSRestored, 0) AS OSRestored,
            u.ObservCodes,
            u.ObservNotes,
            u.Grade
        FROM Lots l
        JOIN Units u ON u.LotID = l.LotID
        -- Display
        LEFT JOIN Units_Devices d1 ON d1.UnitID = u.UnitID AND d1.Category = 'DISPLAY' AND d1.Refurbished = 0
        -- CPU
        LEFT JOIN Units_Devices d2 ON d2.UnitID = u.UnitID AND d2.Category = 'CPU' AND d2.Refurbished = 0
        -- RAM (we'll use MAX to get one value)
        LEFT JOIN Units_Devices d3 ON d3.UnitID = u.UnitID AND d3.Category = 'RAM' AND d3.Refurbished = 0
        -- Storage (first storage device)
        LEFT JOIN (
            SELECT UnitID, Model, Size, Serial, Info1, 
                   ROW_NUMBER() OVER (PARTITION BY UnitID ORDER BY Didx) as rn
            FROM Units_Devices 
            WHERE Category = 'STORAGE' AND Refurbished = 0
        ) d4 ON d4.UnitID = u.UnitID AND d4.rn = 1
        -- Optical drive
        LEFT JOIN Units_Devices d5 ON d5.UnitID = u.UnitID AND d5.Category = 'OPTICAL' AND d5.Refurbished = 0
        -- Keyboard
        LEFT JOIN Units_Devices d6 ON d6.UnitID = u.UnitID AND d6.Category = 'KEYB' AND d6.Refurbished = 0
        -- Webcam
        LEFT JOIN Units_Devices d7 ON d7.UnitID = u.UnitID AND d7.Category = 'WEBCAM' AND d7.Refurbished = 0
        -- Video card
        LEFT JOIN Units_Devices d8 ON d8.UnitID = u.UnitID AND d8.Category = 'VIDEOCARD' AND d8.Refurbished = 0

        WHERE l.Number = %s
        GROUP BY u.UnitID, l.Number, u.AssetTag, u.Created, u.ProductType, u.Model, u.Chassis, 
                 u.PartNumber, u.SerialNumber, d1.Size, d1.Info1, d1.Info2, d2.Model, d2.Speed, d2.Info1,
                 d4.Size, d4.Info1, d4.Model, d4.Serial, d5.Model, d6.Model, d7.Model, d8.Model,
                 u.OSRestored, u.ObservCodes, u.ObservNotes, u.Grade
        ORDER BY u.UnitID
    """

    @api.model
    def lot_exists(self, lot_no):
        """
        Checks if a given lot exists in the Aiken Workbench.
        Returns True if the lot exists, False otherwise.
        """
        conn = None
        exists = False
        try:
            conn = pymysql.connect(**self._dsn())
            with conn.cursor() as cur:
                cur.execute("SELECT 1 FROM Lots WHERE Number = %s LIMIT 1", (lot_no,))
                exists = cur.fetchone() is not None
        except pymysql.err.OperationalError as err:
            _logger.error("MySQL unreachable: %s", err)
            raise UserError(_("Cannot reach Workbench database."))
        except Exception as e:
            _logger.error("Unexpected error checking lot existence: %s", str(e), exc_info=True)
            raise UserError(_("Unexpected error checking lot existence: %s") % str(e))
        finally:
            # Always attempt to close connection if it was opened
            if conn:
                try:
                    conn.close()
                except Exception as close_err:
                    _logger.error("Error closing MySQL connection: %s", str(close_err))
        return exists

    @api.model
    def fetch_audit_for_lot(self, lot_no):
        """
        Fetches all device data for a given lot in a format suitable for the audit report.
        Returns a list of dicts with all required fields for the report.
        """
        # Defensive: Always check lot existence first
        try:
            if not self.lot_exists(lot_no):
                raise UserError(_("Lot %s not found in Workbench.") % lot_no)
        except UserError:
            raise
        except Exception as e:
            _logger.error("Error verifying lot existence: %s", str(e), exc_info=True)
            raise UserError(_("Error verifying lot existence: %s") % str(e))

        conn = None
        raw_rows = []
        try:
            conn = pymysql.connect(**self._dsn())
            with conn.cursor() as cur:
                cur.execute(self._AUDIT_SQL, (lot_no,))
                raw_rows = cur.fetchall() or []
        except pymysql.err.OperationalError as err:
            _logger.error("MySQL unreachable: %s", err)
            raise UserError(_("Cannot reach Workbench database."))
        except Exception as e:
            _logger.error("Unexpected error fetching audit data: %s", str(e), exc_info=True)
            raise UserError(_("Unexpected error fetching audit data: %s") % str(e))
        finally:
            # Always attempt to close connection if it was opened
            if conn:
                try:
                    conn.close()
                except Exception as close_err:
                    _logger.error("Error closing MySQL connection: %s", str(close_err))

        # Always return a list, even if empty
        result = []
        for row in raw_rows:
            try:
                result.append({
                    'unitid': row.get('UnitID'),
                    'lotid': row.get('LotID'),
                    'assettag': row.get('AssetTag'),
                    'created': row.get('Created').strftime('%Y-%m-%d %H:%M:%S') if row.get('Created') else '',
                    'producttype': row.get('ProductType'),
                    'manufacturer': row.get('Manufacturer'),
                    'model': row.get('Model'),
                    'chassis': row.get('Chassis'),
                    'partnumber': row.get('PartNumber'),
                    'serialnumber': row.get('SerialNumber'),
                    'displaysize': row.get('DisplaySize'),
                    'resolution': row.get('Resolution'),
                    'processor': row.get('Processor'),
                    'procspeed': row.get('ProcSpeed'),
                    'procgen': row.get('ProcGen'),
                    'ram': row.get('RAM'),
                    'storage1size': row.get('Storage1Size'),
                    'storage1type': row.get('Storage1Type'),
                    'storage1model': row.get('Storage1Model'),
                    'storage1serial': row.get('Storage1Serial'),
                    'optical': row.get('Optical'),
                    'keyb': row.get('Keyb'),
                    'webcam': row.get('Webcam'),
                    'videocard': row.get('Videocard'),
                    'osrestored': 'Yes' if row.get('OSRestored') else 'No',
                    'obscodes': row.get('ObservCodes'),
                    'observnotes': row.get('ObservNotes'),
                    'grade': row.get('Grade')
                })
            except Exception as row_err:
                _logger.error("Error parsing audit row: %s", str(row_err), exc_info=True)
                continue
        return result

    @api.model
    def _dsn(self):
        """
        Returns the connection parameters for the Aiken Workbench database.
        Reads from environment variables first, then Odoo config parameters.
        """
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
                    'hd_idx': r.get('hd_idx', '-') ,
                    'hd_model': r.get('hd_model', '-') ,
                    'hd_sn': r.get('hd_sn', '-') ,
                    'hd_size': r.get('hd_size', '-') ,
                    'erasure_id': r.get('UnitID', '-') ,
                    'method': method,
                    'timestamp': str(r.get('Audited', '-')),
                })
            except Exception as e:
                _logger.error("Error formatting row for report: %s", str(e), exc_info=True)
                continue

        if not rows:
            raise UserError(_("No erasure records found for lot %s.") % lot_no)
        return rows
