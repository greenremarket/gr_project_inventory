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
        GROUP BY u.UnitID, l.Number, u.AssetTag, u.Created, u.ProductType, u.Manufacturer,
                 u.Model, u.Chassis, u.PartNumber, u.SerialNumber,
                 d1.Size, d1.Info1, d1.Info2, d2.Model, d2.Speed, d2.Info1,
                 d4.Size, d4.Info1, d4.Model, d4.Serial, d5.Model, d6.Model, d7.Model, d8.Model,
                 u.OSRestored, u.ObservCodes, u.ObservNotes, u.Grade
        ORDER BY u.UnitID
    """

    # Reconstructed erasure SQL for fetch_for_lot. Only edit this if the erasure certificate/report fields change.
    _SQL = """
        SELECT
            u.UnitID,
            u.AssetTag,
            u.SerialNumber,
            u.Model,
            d.UnitID AS hd_unitid,
            d.Model AS hd_model,
            d.Serial AS hd_sn,
            d.Size AS hd_size,
            d.Didx AS hd_idx,
            d.Erased AS hd_erased,  -- Explicitly select device erasure status
            u.Audited,
            u.OSRestored
        FROM Units u
        INNER JOIN Lots l ON l.LotID = u.LotID
        LEFT JOIN Units_Devices d ON d.UnitID = u.UnitID AND d.Category = 'STORAGE' AND d.Refurbished = 0
        WHERE l.Number = %s
        ORDER BY u.UnitID, d.Didx
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

        if not raw_rows:
            raise UserError(_("Le lot %s existe dans Aiken mais n'a aucun appareil enregistré pour l'instant.") % lot_no)

        result = []
        for row in raw_rows:
            try:
                # Safely format Created: PyMySQL normally returns datetime objects,
                # but guard against strings or other types just in case.
                created_val = row.get('Created')
                if hasattr(created_val, 'strftime'):
                    created_str = created_val.strftime('%Y-%m-%d %H:%M:%S')
                else:
                    created_str = str(created_val) if created_val else ''

                result.append({
                    'unitid': row.get('UnitID'),
                    'lotid': row.get('LotID'),
                    'assettag': row.get('AssetTag'),
                    'created': created_str,
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
                _logger.error("Error parsing audit row: %s | row keys: %s", str(row_err), list(row.keys()), exc_info=True)
                continue

        if not result and raw_rows:
            raise UserError(_(
                "Lot %s returned %d rows from Workbench but all failed to parse. "
                "Check the Odoo server log for 'Error parsing audit row' entries."
            ) % (lot_no, len(raw_rows)))

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
        host = host or ICP.get_param('gr.workbench_host', '192.168.21.206')
        port = int(port or ICP.get_param('gr.workbench_port', 3306))
        user = user or ICP.get_param('gr.workbench_user', 'awbadmin')
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

    @api.model
    def create_lot(self, lot_name, customer):
        """
        Creates a new lot in the Aiken Workbench MySQL database.

        :param lot_name: The lot number / name string (maps to Lots.Number).
        :param customer: The customer label (maps to Lots.Customer).
        :raises Exception: On connection failure, duplicate lot, or any MySQL error.
                           The caller is responsible for deciding whether to surface
                           this as a blocking error or a non-blocking notification.
        """
        _PARAMS_SIZE = 352  # observed fixed size in production rows
        _PARAMS_BLOB = b'0' * _PARAMS_SIZE

        conn = None
        try:
            conn = pymysql.connect(**self._dsn())
            conn.autocommit = False
            with conn.cursor() as cur:
                # 1. Fail fast if the lot already exists
                cur.execute(
                    "SELECT 1 FROM Lots WHERE Number = %s LIMIT 1",
                    (lot_name,),
                )
                if cur.fetchone() is not None:
                    raise ValueError(
                        "Lot '%s' already exists in Aiken Workbench." % lot_name
                    )

                # 2. Allocate next LotID (no AUTO_INCREMENT on this table)
                cur.execute("SELECT COALESCE(MAX(LotID), 0) + 1 AS next_id FROM Lots")
                row = cur.fetchone()
                next_id = row['next_id']

                # 3. Insert the new lot row
                cur.execute(
                    """
                    INSERT INTO Lots
                        (LotID, Number, Owner, Customer, Description,
                         Status, Params, Created, Uploaded)
                    VALUES
                        (%s, %s, 'AIKEN', %s, 'AUDIT EFFACEMENT',
                         0, %s, NOW(), NULL)
                    """,
                    (next_id, lot_name, customer or '', _PARAMS_BLOB),
                )
            conn.commit()
            _logger.info(
                '[aiken] create_lot: inserted Lots row LotID=%s Number=%s Customer=%s',
                next_id, lot_name, customer,
            )
        except Exception:
            if conn:
                try:
                    conn.rollback()
                except Exception as rb_err:
                    _logger.error('[aiken] create_lot: rollback failed: %s', rb_err)
            raise
        finally:
            if conn:
                try:
                    conn.close()
                except Exception as cl_err:
                    _logger.error('[aiken] create_lot: close failed: %s', cl_err)

    def fetch_for_lot(self, lot_no):
        """
        Fetches erasure data for a given lot from the Aiken Workbench.
        Returns a list of dicts ready for the report, with all required fields and error handling.
        Bulletproofed: follows Odoo 17 best practices and matches guardrails of fetch_audit_for_lot.
        """
        _t = _  # Never shadow _ for translations
        # Prepare DSN and log (never log password)
        dsn = self._dsn().copy()
        dsn_log = dsn.copy(); dsn_log['password'] = '***'
        _logger.info(f"[fetch_for_lot] DSN: {dsn_log}, lot_no: {lot_no}")
        conn = None
        raw_rows = []
        try:
            conn = pymysql.connect(**dsn)
            with conn.cursor() as cur:
                cur.execute(self._SQL, (lot_no,))
                raw_rows = cur.fetchall() or []
        except pymysql.err.OperationalError as err:
            _logger.error(f"MySQL unreachable for DSN {dsn_log}: {err}")
            raise UserError(_t("Cannot reach Workbench database at %(host)s:%(port)s as %(user)s (DB: %(database)s). Please contact your administrator.") % dsn_log)
        except Exception as e:
            _logger.error(f"Unexpected error fetching erasure data for lot '{lot_no}' with DSN {dsn_log}: {str(e)}", exc_info=True)
            raise UserError(_t("Unexpected error fetching erasure data for lot %s: %s") % (lot_no, str(e)))
        finally:
            # Always attempt to close connection if it was opened
            if conn:
                try:
                    conn.close()
                except Exception as close_err:
                    _logger.error(f"Error closing MySQL connection for DSN {dsn_log}: {str(close_err)}")

        # Distinguish between "lot doesn't exist" and "lot exists but has no units".
        # _SQL starts from Units so it returns nothing for an empty lot — same as a missing lot.
        if not raw_rows:
            if self.lot_exists(lot_no):
                raise UserError(_t(
                    "Le lot %s existe dans Aiken mais n'a aucun appareil enregistré pour l'instant."
                ) % lot_no)
            raise UserError(_t("Lot %s introuvable dans Aiken Workbench.") % lot_no)

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
                # Double rail guard: robustly check for device erasure status
                erased_val = None
                try:
                    # First, prefer explicit hd_erased field from SQL
                    if 'hd_erased' in r:
                        erased_val = r['hd_erased']
                    # Fallback to Erased if present (legacy)
                    elif 'Erased' in r:
                        erased_val = r['Erased']
                except Exception as guard_err:
                    _logger.error(f"[fetch_for_lot] Error extracting erasure status for row: {r}. Error: {guard_err}", exc_info=True)
                    erased_val = None
                # Final fallback and type check
                if erased_val is None:
                    erasure_status = 'Unknown'
                    _logger.warning(f"[fetch_for_lot] Device erasure status missing for row: {r}")
                else:
                    try:
                        erased_int = int(erased_val)
                        erasure_status = 'Erased' if erased_int else 'Not Erased'
                    except Exception as conv_err:
                        erasure_status = 'Unknown'
                        _logger.warning(f"[fetch_for_lot] Device erasure status not int for row: {r} (got: {erased_val}). Error: {conv_err}")
                # Method: use OSRestored as a proxy, or always 'Unknown'
                osrestored = r.get('OSRestored', '')
                method = 'Zeros' if osrestored and str(osrestored).strip() else 'Unknown'
                # Compose row for report, now including robust erasure status
                rows.append({
                    'host_machine': host_machine,
                    'hd_idx': r.get('hd_idx', '-') ,
                    'hd_model': r.get('hd_model', '-') ,
                    'hd_sn': r.get('hd_sn', '-') ,
                    'hd_size': r.get('hd_size', '-') ,
                    'erasure_id': r.get('UnitID', '-') ,
                    'method': method,
                    'erasure_status': erasure_status,
                    'timestamp': str(r.get('Audited', '-')),
                })

            except Exception as e:
                _logger.error(f"Error formatting row for report for lot '{lot_no}': {str(e)}", exc_info=True)
                continue

        # Filter to only include drives that HAVE been erased
        erased_rows = [row for row in rows if row.get('erasure_status') == 'Erased']
        # If no valid erased rows were parsed, inform the user
        if not erased_rows:
            raise UserError(_t("No erased drives found for lot %s.") % lot_no)
        return erased_rows  # Only return erased drives
