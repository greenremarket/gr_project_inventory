import socket
import logging
from datetime import datetime, timedelta, date, time as dt_time
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import threading
import re

_logger = logging.getLogger(__name__)  # Correct logger definition

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    module_gr_project_inventory = fields.Boolean(
        string="Project Inventory Module",
        help="Enable functionalities from the Project Inventory module."
    )

    printer_ip = fields.Char(string="Zebra Printer IP Address", config_parameter='gr_project_inventory.printer_ip')
    printer_port = fields.Integer(string="Zebra Printer Port", config_parameter='gr_project_inventory.printer_port', default=9100)


class GrChassis(models.Model):
    _name = 'gr.chassis'
    _description = 'Chassis'
    _order = 'name asc'

    name = fields.Char(string='Chassis', required=True, index=True)

    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'This chassis already exists!')
    ]


class GrObservation(models.Model):
    _name = 'gr.observation'
    _description = 'Inventory Observations'
    _order = 'name asc'

    name = fields.Char(string='Observation', required=True, index=True)

    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'This observation already exists!')
    ]

    @api.model_create_multi
    def create(self, vals_list):
        """Override create to automatically convert observation names to uppercase"""
        for vals in vals_list:
            if vals.get('name'):
                vals['name'] = vals['name'].strip().upper()
        return super(GrObservation, self).create(vals_list)

    def write(self, vals):
        """Override write to automatically convert observation names to uppercase"""
        if vals.get('name'):
            vals['name'] = vals['name'].strip().upper()
        return super(GrObservation, self).write(vals)


class GrProductType(models.Model):
    _name = "gr.product.type"
    _description = "Product Type"
    _order = "name asc"

    name = fields.Char(string="Product Type", required=True, index=True)

    _sql_constraints = [
        ('unique_product_type_name', 'unique(name)', 'Product type name must be unique.'),
    ]

class GrDeliverable(models.Model):
    _name = 'gr.deliverable'
    _description = 'Deliverables'

    name = fields.Char(string='Deliverables', required=True, translate=True)


class GrClientInventory(models.Model):
    _name = 'gr.client.inventory'
    _description = 'Client Inventory'

    name = fields.Char(string='Name', required=True)
    serial_number = fields.Char(string='Serial Number')
    asset_tag = fields.Char(string='Asset Tag')
    pallet_number = fields.Char(string='Pallet Number')
    task_id = fields.Many2one(
        comodel_name='project.task',
        string='Task',
        ondelete='cascade',
        required=True,
        index=True,
    )
    select_item = fields.Boolean(string='Selected', default=False)
    internal_inventory_id = fields.Many2one(
        'gr.internal.inventory',
        string='Internal Inventory',
        readonly=True
    )

    # Nouveaux champs Many2one
    product_type_id = fields.Many2one('gr.product.type', string='Product Type')
    chassis_id = fields.Many2one('gr.chassis', string='Chassis')
    manufacturer_id = fields.Many2one(
        'gr.manufacturer',
        string='Manufacturer',
        ondelete='restrict'
    )

    def action_create_internal_inventory(self):
        self.ensure_one()
        if self.internal_inventory_id:
            # Ouvrir l'inventaire interne existant
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'gr.internal.inventory',
                'view_mode': 'form',
                'res_id': self.internal_inventory_id.id,
                'target': 'current',
            }
        else:
            # Ouvrir le wizard pour créer un nouvel inventaire interne
            return {
                'name': 'Créer un inventaire interne',
                'type': 'ir.actions.act_window',
                'res_model': 'internal.inventory.wizard',
                'view_mode': 'form',
                'target': 'new',
                'context': {
                    'default_client_inventory_id': self.id,
                },
            }

    def action_view_internal_inventory(self):
        self.ensure_one()
        internal_inventory = self.env['gr.internal.inventory'].search([
            ('client_inventory_id', '=', self.id)
        ], limit=1)
        if (internal_inventory):
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'gr.internal.inventory',
                'view_mode': 'form',
                'res_id': internal_inventory.id,
                'target': 'current',
            }
        else:
            raise UserError("Aucun inventaire interne associé.")

from odoo import models, fields, api, _
from odoo.exceptions import UserError


# Import centralized config (gr_portal must be installed)
try:
    from odoo.addons.gr_portal.const import DELIVERABLE_CONFIG
except ImportError:
    import logging as _logging
    _logging.getLogger(__name__).warning(
        "gr_portal not installed — deliverable indicators disabled. "
        "Install gr_portal to enable has_*/count_* fields on project.task."
    )
    DELIVERABLE_CONFIG = {}

class InternalInventoryWizard(models.TransientModel):
    _name = 'internal.inventory.wizard'
    _description = 'Wizard for Creating Internal Inventory from Client Inventory'
    _inherit = ['mail.thread', 'mail.activity.mixin']  # Ajout de l'héritage

    client_inventory_id = fields.Many2one('gr.client.inventory', required=True)
    status = fields.Selection([
        ('REFURB', 'Refurbished'),
        ('NEW', 'New'),
        ('NEW-OPEN-BOX', 'New Open Box'),
        ('TBD', 'TBD')
    ], string='Status', default='TBD', required=True)
    
    observation_id = fields.Many2one(
        'gr.observation',
        string='Observation',
        ondelete='restrict'
    )
    
    name = fields.Char(string='Name', required=True)
    serial_number = fields.Char(string='Serial Number')
    asset_tag = fields.Char(string='Internal Asset Tag', readonly=False)
    part_number = fields.Char(string='Part Number')
    # Ancien champ texte 'chassis' remplacé par le Many2one ci-dessous
    # pour une recherche incrémentale
    product_type_id = fields.Many2one('gr.product.type', string='Product Type')
    chassis_id = fields.Many2one('gr.chassis', string='Chassis')
    manufacturer_id = fields.Many2one(
        'gr.manufacturer',
        string='Manufacturer',
        ondelete='restrict'
    )
    wareh_location = fields.Char(string='Warehouse Location')
    pallet_number = fields.Char(string='Pallet Number')

    internal_inventory_id = fields.Many2one(
        'gr.internal.inventory',
        string="Created Internal Inventory",
        readonly=True
    )

    print_job_ids = fields.One2many(
        'gr.print.job',
        compute='_compute_print_jobs',
        string='Historique d\'impressions'
    )

    @api.model
    def default_get(self, fields_list):
        defaults = super(InternalInventoryWizard, self).default_get(fields_list)
        
        # Check if we're coming from an internal inventory (editing mode)
        inventory_id = self.env.context.get('active_id')
        model = self.env.context.get('active_model')
        
        if model == 'gr.internal.inventory' and inventory_id:
            inventory = self.env['gr.internal.inventory'].browse(inventory_id)
            defaults.update({
                'name': inventory.name,
                'serial_number': inventory.serial_number,
                'pallet_number': inventory.pallet_number,
                'manufacturer_id': inventory.manufacturer_id.id if inventory.manufacturer_id else False,
                'product_type_id': inventory.product_type_id.id if inventory.product_type_id else False,
                'chassis_id': inventory.chassis_id.id if inventory.chassis_id else False,
                'wareh_location': inventory.wareh_location,
                'part_number': inventory.part_number,
                'asset_tag': inventory.asset_tag,
                'status': inventory.status,
                'observation_id': inventory.observation_id.id if inventory.observation_id else False,
                'client_inventory_id': inventory.client_inventory_id.id if inventory.client_inventory_id else False,
                'internal_inventory_id': inventory.id,
            })
        # Check if we're coming from a client inventory (creation mode)
        elif model == 'gr.client.inventory' and inventory_id:
            client_inv = self.env['gr.client.inventory'].browse(inventory_id)
            defaults.update({
                'client_inventory_id': client_inv.id,
                'name': client_inv.name,
                'serial_number': client_inv.serial_number,
                'product_type_id': client_inv.product_type_id.id if client_inv.product_type_id else False,
                'chassis_id': client_inv.chassis_id.id if client_inv.chassis_id else False,
                'manufacturer_id': client_inv.manufacturer_id.id if client_inv.manufacturer_id else False,
                'pallet_number': client_inv.pallet_number,
                'status': 'TBD',  # Default value for new items
            })
            
        return defaults

    def _compute_print_jobs(self):
        for rec in self:
            rec.print_job_ids = self.env['gr.print.job'].search([
                ('asset_tag', '=', rec.asset_tag)
            ], order='print_date desc', limit=10)
    def action_submit(self):
        self.ensure_one()
        if self.internal_inventory_id:
            raise UserError("Already created.")
    
        if not self.client_inventory_id.task_id:
            raise UserError("No Task found on the client inventory.")
    
        vals = {
            'name': self.name,
            'serial_number': self.serial_number,
            'client_asset_tag': self.client_inventory_id.asset_tag,
            'task_id': self.client_inventory_id.task_id.id,
            'part_number': self.part_number,
            'manufacturer_id': self.manufacturer_id.id if self.manufacturer_id else False,
            'product_type_id': self.product_type_id.id if self.product_type_id else False,
            'chassis_id': self.chassis_id.id if self.chassis_id else False,
            'wareh_location': self.wareh_location,
            'pallet_number': self.pallet_number,
            'client_inventory_id': self.client_inventory_id.id,
            'status': self.status,
            'observation_id': self.observation_id.id if self.observation_id else False
        }
        new_internal = self.env['gr.internal.inventory'].create(vals)
        self.internal_inventory_id = new_internal.id
        self.asset_tag = new_internal.asset_tag
    
        self.client_inventory_id.internal_inventory_id = new_internal.id
    
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'internal.inventory.wizard',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
        }

    def action_edit(self):
        self.ensure_one()
        if self.internal_inventory_id:
            vals = {
                'name': self.name,
                'serial_number': self.serial_number,
                'part_number': self.part_number,
                'manufacturer_id': self.manufacturer_id.id if self.manufacturer_id else False,
                'product_type_id': self.product_type_id.id if self.product_type_id else False,
                'chassis_id': self.chassis_id.id if self.chassis_id else False,
                'wareh_location': self.wareh_location,
                'pallet_number': self.pallet_number,
                'status': self.status,
                'observation_id': self.observation_id.id if self.observation_id else False
            }
            self.internal_inventory_id.write(vals)

        # On recharge le wizard, toujours en modal
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'internal.inventory.wizard',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
        }

    def _send_zpl_to_printer(self):
        # You already have self (the wizard recordset) in the same environment.

        _logger.debug("Synchronous _send_zpl_to_printer started.")
        if not self.exists():
            _logger.error("Wizard record does not exist anymore.")
            return

        if not self.asset_tag:
            self.message_post(
                body="Erreur : L\'étiquette d\'actif n\'est pas définie.",
                subtype_id=self.env.ref('mail.mt_warning').id
            )
            return

        zpl = (
            "^XA\n"
            "^FO50,50^BY2\n"
            "^BCN,100,Y,N,N\n"
            f"^FD{self.asset_tag}^FS\n"
            "^XZ\n"
        )

        ip = self.env['ir.config_parameter'].sudo().get_param('gr_project_inventory.printer_ip', '192.168.0.100')
        port = int(self.env['ir.config_parameter'].sudo().get_param('gr_project_inventory.printer_port', '9100'))

        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)  # 5-second timeout
            sock.connect((ip, port))
            sock.sendall(zpl.encode('utf-8'))
            sock.close()

            self.message_post(
                body="Le job d\'impression de code-barres a été exécuté avec succès (synchronement).",
                subtype_id=self.env.ref('mail.mt_note').id
            )
            _logger.info("Tentative d\'envoi de ZPL vers l\'imprimante IP: %s, Port: %s", ip, port)

        except socket.timeout:
            _logger.error(f"Connexion à l\'imprimante à {ip}:{port} expirée.")
            self.message_post(
                body="Erreur : Le délai de connexion à l\'imprimante a expiré.",
                subtype_id=self.env.ref('mail.mt_warning').id
            )

        except Exception as e:
            _logger.exception("Échec de l\'envoi du ZPL à l\'imprimante :")
            self.message_post(
                body="Le job d\'impression de code-barres a échoué.",
                subtype_id=self.env.ref('mail.mt_warning').id
        )
            raise UserError(_("Erreur d\'impression : %s") % str(e))

    def action_print_barcode(self):
        """Imprime le code-barres en appelant la méthode du service Zebra."""
        if not self.internal_inventory_id:
            raise UserError(_("Aucun inventaire interne à imprimer."))
        if not self.asset_tag:
            raise UserError(_("Aucun asset tag à imprimer."))

        # 1) Générer le ZPL
        printer = self.env['gr.zebra.printer']
        zpl_content = printer.generate_asset_tag_zpl(self.asset_tag)

        # 2) Créer un enregistrement d'historique d'impression
        print_job = self.env['gr.print.job'].create({
            'asset_tag': self.asset_tag,
            'zpl_data': zpl_content,
            'internal_inventory_id': self.internal_inventory_id.id,
            'status': 'pending'
        })

        # 3) Tenter l'envoi à l'imprimante
        try:
            printer._send_zpl(zpl_content)
            print_job.write({'status': 'success'})
            self.message_post(
                body="Le code-barres a été imprimé avec succès.",
                subtype_id=self.env.ref('mail.mt_note').id
            )
        except UserError as e:
            print_job.write({
                'status': 'failed',
                'error_message': str(e)
            })
            # Récupère le subtype warning s'il existe
            warning_subtype = self.env.ref('mail.mt_warning', raise_if_not_found=False)
            subtype_id = warning_subtype.id if warning_subtype else False
            self.message_post(
                body="Échec d\'impression : %s" % str(e),
                subtype_id=subtype_id
            )
            raise

        return True

    def action_close(self):
        _logger.debug("Action Close initiated.")
        return {'type': 'ir.actions.act_window_close'}

class GrInternalInventory(models.Model):
    _name = 'gr.internal.inventory'
    _description = 'Internal Inventory'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'created_at desc'  # Sort by creation time, newest first

    @api.model
    def _get_relevant_barcode_records(self, barcode):
        return self.search([('asset_tag', '=', barcode)], limit=1)

    @api.model
    def _barcode_product_action(self, barcode):
        """
        Method called by the barcode scanning system when a barcode of type 'product' is scanned.
        This method will be called for barcodes matching our pattern GI/
        """
        # Additional validation to ensure it matches our full pattern
        if not re.match(r'^GI/[^/]+/\d{6}$', barcode):
            raise UserError(_("Invalid asset tag format. Expected format: GI/prefix/123456"))
        
        return self.open_by_asset_tag(barcode)

    name = fields.Char(string='Nom', required=True)
    serial_number = fields.Char(string='Numéro de Série')
    client_asset_tag = fields.Char(
        string='Asset Tag Client',
        compute='_compute_client_asset_tag',
        store=True,  # Important pour la recherche et le tri
    )
    pallet_number = fields.Char(string='Pallet Number')
    wareh_location = fields.Char(string='Warehouse Location')
    part_number = fields.Char(string='Part Number')

    task_id = fields.Many2one(
        comodel_name='project.task',
        string='Tâche',
        ondelete='cascade',
        required=True,
        index=True,
    )
    asset_tag = fields.Char(string='Asset Tag Interne', readonly=False, copy=False)

    client_inventory_id = fields.Many2one(
        comodel_name='gr.client.inventory',
        string='Client Inventory',
        ondelete='set null',
        index=True,
    )

    status = fields.Selection([
        ('REFURB', 'Refurbished'),
        ('NEW', 'New'),
        ('NEW-OPEN-BOX', 'New Open Box'),
        ('TBD', 'TBD')
    ], string='Status', default='TBD', required=True, tracking=True)

    observation_id = fields.Many2one(
        'gr.observation',
        string='Observation',
        ondelete='restrict',
        tracking=True,
        help="Observations about the item's condition or missing components"
    )

    # Nouveaux champs Many2one en remplacement ou en complément de « chassis »
    product_type_id = fields.Many2one('gr.product.type', string='Product Type')
    chassis_id = fields.Many2one('gr.chassis', string='Chassis')
    manufacturer_id = fields.Many2one(
        'gr.manufacturer',
        string='Manufacturer',
        ondelete='restrict'
    )

    created_at = fields.Datetime(
        string='Date de création',
        default=fields.Datetime.now,
        required=True,  # Remettre required=True pour assurer que le champ n'est jamais vide
        copy=False,  # Lors de la duplication, utiliser la date actuelle au lieu de copier l'originale
        index=True,  # Used by _order = 'created_at desc' — index avoids full-scan sort on large sets
    )

    # Ajouter ce nouveau champ
    created_by_id = fields.Many2one(
        'res.users',
        string='Créé par',
        readonly=True,
        default=lambda self: self.env.user.id,
        tracking=True,  # Pour suivre les changements dans le chatter
        copy=False,  # Lors de la duplication, utiliser l'utilisateur actuel au lieu de copier l'original
    )

    inventory_line_ids = fields.One2many(
        comodel_name='gr.internal.inventory',
        inverse_name='task_id',
        string='Internal Inventory Lines',
    )

    @api.depends('client_inventory_id.asset_tag')
    def _compute_client_asset_tag(self):
        for record in self:
            record.client_asset_tag = record.client_inventory_id.asset_tag if record.client_inventory_id else False

    @api.model
    def create(self, vals):
        # Ajouter l'utilisateur courant si non spécifié
        if 'created_by_id' not in vals:
            vals['created_by_id'] = self.env.user.id
            
        # Conserver le code existant pour la génération de l'asset_tag
        if 'asset_tag' not in vals or not vals['asset_tag']:
            task = self.env['project.task'].browse(vals.get('task_id'))
        if task:
            task.last_asset_tag_number += 1
            last_number = task.last_asset_tag_number
            # Utiliser lot_name s'il existe, sinon utiliser une valeur par défaut
            if task.lot_name:
                vals['asset_tag'] = f"GI/{task.lot_name}/{last_number:06d}"
            else:
                # On n'utilise plus "TASK" + ID, mais on exige que lot_name soit défini
                raise ValidationError("Impossible de générer l'asset tag: le nom du lot (lot_name) n'est pas défini sur cette tâche.")
        
        # S'assurer que created_at est défini
        if 'created_at' not in vals:
            vals['created_at'] = fields.Datetime.now()

        return super(GrInternalInventory, self).create(vals)

    def action_validate(self):
        self.ensure_one()
        return {'type': 'ir.actions.act_window_close'}

    def action_cancel(self):
        self.ensure_one()
        self.unlink()
        return {'type': 'ir.actions.act_window_close'}

    def unlink(self):
        for record in self:
            if record.client_inventory_id:
                record.client_inventory_id.select_item = False
        return super(GrInternalInventory, self).unlink()

    def open_by_asset_tag(self, barcode_value):
        """
        Appelée par la règle barcodes pour un code qui match '^gr-.*'
        'barcode_value' contient la valeur brute scannée.
        """
        # Rechercher l'enregistrement correspondant
        record = self.search([('asset_tag', '=', barcode_value)], limit=1)
        if not record:
            raise UserError(f"No inventory found for asset tag: {barcode_value}")

        # Retourner une action pour ouvrir le form
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'gr.internal.inventory',
            'view_mode': 'form',
            'res_id': record.id,
            'target': 'current',
        }

    def action_print_barcode(self):
        self.ensure_one()
        if not self.asset_tag:
            raise UserError(_("Le champ 'Asset Tag' est vide."))

        # 1) Générer le ZPL via le service Zebra
        printer = self.env['gr.zebra.printer']
        zpl_content = printer.generate_asset_tag_zpl(self.asset_tag)

        # 2) Créer un enregistrement d'historique d'impression
        print_job = self.env['gr.print.job'].create({
            'asset_tag': self.asset_tag,
            'zpl_data': zpl_content,
            'internal_inventory_id': self.id,
            'status': 'pending'
        })

        # 3) Envoyer à l'imprimante
        try:
            printer._send_zpl(zpl_content)
            print_job.write({'status': 'success'})
        except Exception as e:
            print_job.write({'status': 'failed', 'error_message': str(e)})
            raise UserError(_("Erreur d\'impression : %s") % str(e))

        return True

    def action_duplicate_line(self):
        self.ensure_one()
        # Créer une copie avec les champs voulus vides
        new_record = self.copy({
            'serial_number': False,
            'asset_tag': False,
            'created_at': fields.Datetime.now(),  # Utiliser la date actuelle
            'created_by_id': self.env.user.id,   # Utiliser l'utilisateur actuel
        })
        # Pas de retour d'action, la ligne sera ajoutée directement dans la vue tree
        return True

    def action_duplicate_line_in_act_window(self):
        self.ensure_one()
        # Créer une copie avec les champs voulus vides
        new_record = self.copy({
            'serial_number': False,
            'asset_tag': False,
            'created_at': fields.Datetime.now(),  # Utiliser la date actuelle
            'created_by_id': self.env.user.id,   # Utiliser l'utilisateur actuel
        })
        
        # Retourner une action qui ouvre la vue en mode édition sur la nouvelle ligne
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'gr.internal.inventory',
            'view_mode': 'form',
            'res_id': new_record.id,
            'target': 'new',
            'context': {
                'form_view_initial_mode': 'edit',
                'force_detailed_view': True
            },
            'flags': {
                'form': {
                    'action_buttons': True
                }
            }
        }

    @api.model
    def barcode_scan(self, barcode):
        """Handle barcode scanning for internal inventory items"""
        record = self.search([('asset_tag', '=', barcode)], limit=1)
        if not record:
            raise UserError(_("No internal inventory found for asset tag: %s") % barcode)
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'gr.internal.inventory',
            'view_mode': 'form',
            'res_id': record.id,
            'target': 'current',
        }

    @api.model
    def _init_created_at_for_existing_records(self):
        # Trouver tous les enregistrements sans created_at
        records_without_date = self.search([('created_at', '=', False)])
        if records_without_date:
            # Mettre à jour avec la date actuelle
            records_without_date.write({'created_at': fields.Datetime.now()})
        return True

    @api.onchange('internal_inventory_search')
    def _onchange_internal_inventory_search(self):
        """Applique un domaine à 'internal_inventory_filtered_ids'"""
        if self.internal_inventory_search:
            search_str = self.internal_inventory_search.strip()
            return {
                'domain': {
                    'internal_inventory_filtered_ids': [
                        '|', '|',
                        ('serial_number', 'ilike', search_str),
                        ('asset_tag', 'ilike', search_str),
                        ('pallet_number', 'ilike', search_str)
                    ]
                }
            }
        else:
            return {'domain': {'internal_inventory_filtered_ids': []}}

    internal_inventory_search = fields.Char(string="Search")
    
    def action_add_internal_inventory_line(self):
        """Ouvre un formulaire pour créer une nouvelle ligne d'inventaire interne"""
        self.ensure_one()
        return {
            'name': _("Ajouter une ligne d'inventaire"),
            'type': 'ir.actions.act_window',
            'res_model': 'gr.internal.inventory',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_task_id': self.id,
            }
        }

    @api.depends('inventory_line_ids')
    def _compute_internal_inventory_count(self):
        for task in self:
            task.internal_inventory_count = len(task.inventory_line_ids)

    @api.depends('inventory_line_ids')
    def _compute_internal_inventory_tab_title(self):
        for task in self:
            count = len(task.inventory_line_ids)
            task.internal_inventory_tab_title = f"Internal Inventory ({count})"

    @api.depends('client_inventory_ids')
    def _compute_client_inventory_count(self):
        for task in self:
            task.client_inventory_count = len(task.client_inventory_ids)

    @api.depends('discrepancies_ids.discrepancy_type', 'discrepancies_ids.resolved')
    def _compute_discrepancy_type_counts(self):
        for task in self:
            # Compter uniquement les discrepancies non résolues
            unresolved_discrepancies = task.discrepancies_ids.filtered(lambda d: not d.resolved)
            
            # Compter par type
            task.missing_items_count = len(unresolved_discrepancies.filtered(lambda d: d.discrepancy_type == 'missing'))
            task.extra_items_count = len(unresolved_discrepancies.filtered(lambda d: d.discrepancy_type == 'extra'))

    @api.model
    def _migrate_partner_to_destination_name(self):
        # Récupérer les tâches qui ont un partenaire mais pas de client_destination_name
        tasks = self.search([
            ('client_destination_name', '=', False),
            ('partner_id', '!=', False)
        ])
        
        success_count = 0
        total_count = len(tasks)
        failed_ids = []
        
        for task in tasks:
            try:
                if task.partner_id:
                    task.client_destination_name = task.partner_id.name
                    success_count += 1
            except Exception as e:
                failed_ids.append((task.id, str(e)))
                continue
        
        return {
            'total': total_count,
            'success': success_count,
            'failed': failed_ids
        }

class GrZebraPrinter(models.Model):
    _name = 'gr.zebra.printer'
    _description = 'Zebra Printer Service'

    def _send_zpl(self, zpl_content):
        """Centralise l'envoi du ZPL à l'imprimante Zebra."""
        ip = self.env['ir.config_parameter'].sudo().get_param('gr_project_inventory.printer_ip', '192.168.21.149')
        port = int(self.env['ir.config_parameter'].sudo().get_param('gr_project_inventory.printer_port', 9100))
        _logger.info("Tentative d\'envoi de ZPL vers l\'imprimante IP: %s, Port: %s", ip, port)
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(5)
                sock.connect((ip, port))
                sock.sendall(zpl_content.encode('utf-8'))
        except Exception as e:
            _logger.error("Erreur d\'impression ZPL vers IP: %s, Port: %s. Erreur: %s", ip, port, e)
            raise UserError(_("Impossible d\'imprimer : %s") % str(e))

    def generate_asset_tag_zpl(self, asset_tag):
        """
        Génère un code-barres Code 128 plus grand avec texte identique.
        """
        zpl = f"""
^XA
^PW480
^LL310
^LS0
^LH0,0
^MMT
^MNW
^CF0,45

^BY2,3,250                
^FO5,40^BCN,250,N,N,N^FD{asset_tag}^FS
^CF0,40
^FO5,290^FD{asset_tag}^FS  
^XZ"""
        return zpl


class GrPrintJob(models.Model):
    _name = 'gr.print.job'
    _description = 'Historique des impressions'

    print_date = fields.Datetime(default=fields.Datetime.now)
    asset_tag = fields.Char(string='Asset Tag')
    zpl_data = fields.Text(string='ZPL Data')
    status = fields.Selection([
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed'),
    ], default='pending')
    error_message = fields.Text(string='Erreur')
    internal_inventory_id = fields.Many2one('gr.internal.inventory', string='Inventaire Interne')

    def action_reprint(self):
        """Permet de réimprimer depuis l'historique existant."""
        self.ensure_one()
        printer = self.env['gr.zebra.printer']
        try:
            printer._send_zpl(self.zpl_data)
            self.write({'status': 'success'})
        except UserError as e:
            self.write({'status': 'failed', 'error_message': str(e)})
            raise

class GrManufacturer(models.Model):
    _name = 'gr.manufacturer'
    _description = 'Manufacturer'
    _order = 'name asc'

    name = fields.Char(string='Manufacturer', required=True)
    
    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'Manufacturer name must be unique!')
    ]

class GrDiscrepancy(models.Model):
    _name = 'gr.discrepancy'
    _description = 'Inventory Discrepancy'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(string='Description', required=True)
    discrepancy_type = fields.Selection([
        ('missing', 'Missing Item'),
        ('extra', 'Extra Item'),
        ('damaged', 'Damaged Item'),
        ('wrong', 'Wrong Item')
    ], string='Type', required=True, default='missing')
    
    task_id = fields.Many2one(
        'project.task',
        string='Task',
        required=True,
        ondelete='cascade'
    )
    
    internal_inventory_id = fields.Many2one(
        'gr.internal.inventory',
        string='Internal Inventory Item',
        ondelete='set null'
    )
    
    client_inventory_id = fields.Many2one(
        'gr.client.inventory',
        string='Client Inventory Item',
        ondelete='set null'
    )
    
    # Champs manquants référencés dans les vues XML
    serial_number = fields.Char(string='Serial Number')
    asset_tag = fields.Char(string='Asset Tag')
    pallet_number = fields.Char(string='Pallet Number')
    manufacturer_id = fields.Many2one('gr.manufacturer', string='Manufacturer')
    product_type_id = fields.Many2one('gr.product.type', string='Product Type')
    chassis_id = fields.Many2one('gr.chassis', string='Chassis')
    
    notes = fields.Text(string='Notes')
    resolved = fields.Boolean(string='Resolved', default=False)
    resolution_date = fields.Datetime(string='Resolution Date')
    resolution_notes = fields.Text(string='Resolution Notes')
    
    @api.model
    def create(self, vals):
        if not vals.get('name'):
            if vals.get('discrepancy_type') == 'missing':
                vals['name'] = 'Missing Item'
            elif vals.get('discrepancy_type') == 'extra':
                vals['name'] = 'Extra Item'
            elif vals.get('discrepancy_type') == 'damaged':
                vals['name'] = 'Damaged Item'
            elif vals.get('discrepancy_type') == 'wrong':
                vals['name'] = 'Wrong Item'
        return super(GrDiscrepancy, self).create(vals)
    
    def action_mark_resolved(self):
        self.write({
            'resolved': True,
            'resolution_date': fields.Datetime.now()
        })
        return True
    
    def action_mark_unresolved(self):
        self.write({
            'resolved': False,
            'resolution_date': False,
            'resolution_notes': False
        })
        return True

# Ajouter la classe ProjectTask qui hérite de project.task
class ProjectTask(models.Model):
    _inherit = 'project.task'
    # Override project_id to set default to "General" project
    project_id = fields.Many2one(
        'project.project',
        default=lambda self: self._get_default_project(),
        string='Project'
    )
    
    def _get_default_project(self):
        """Set default project to the project named 'General'."""
        general_project = self.env['project.project'].search([
            ('name', '=', 'General')
        ], limit=1)
        return general_project if general_project else False


    # Champs requis qui ont disparu
    order_giver_id = fields.Many2one(
        'res.partner',
        string='Order Giver',
        tracking=True
    )
    
    client_destination_name = fields.Char(
        string='Client Destination Name',
        tracking=True
    )
    
    # Ajout du champ contacts manquant
    contacts = fields.Char(
        string='Contacts',
        help="Informations de contact liées à l'opération."
    )
    
    # Ajout du champ address manquant
    address = fields.Text(
        string="Addresse de l'opération",
        help='Adresse liée à l\'opération.'
    )
    
    # Ajout du champ deliverable_ids manquant
    deliverable_ids = fields.Many2many(
        'gr.deliverable',
        string='Deliverables',
        help='Livrables associés à cette tâche.'
    )
    
    # Autres champs existants
    lot_name = fields.Char(string='Lot Name')
    create_aiken_lot = fields.Boolean(
        string='Créer le lot Aiken',
        default=False,
        help='Si coché, crée automatiquement le lot correspondant dans Aiken Workbench à la création de la tâche.',
    )
    last_asset_tag_number = fields.Integer(string='Last Asset Tag Number', default=0)
    
    # Champs pour l'inventaire interne
    internal_inventory_count = fields.Integer(
        string='Internal Inventory Count',
        compute='_compute_internal_inventory_count',
        store=False
    )
    
    internal_inventory_search = fields.Char(
        string='Search Internal Inventory',
        store=False
    )
    
    internal_inventory_filtered_ids = fields.One2many(
        'gr.internal.inventory',
        'task_id',
        string='Filtered Internal Inventory',
        compute='_compute_internal_inventory_filtered_ids',
    )
    
    # Ajoutez ce champ avant la définition de internal_inventory_filtered_ids
    inventory_line_ids = fields.One2many(
        'gr.internal.inventory',
        'task_id',
        string='Internal Inventory Lines'
    )
    
    @api.depends('internal_inventory_search', 'inventory_line_ids.serial_number', 
                'inventory_line_ids.asset_tag', 'inventory_line_ids.pallet_number')
    def _compute_internal_inventory_filtered_ids(self):
        for task in self:
            if task.internal_inventory_search:
                search_str = task.internal_inventory_search.lower()
                filtered_records = task.inventory_line_ids.filtered(
                    lambda r: (r.serial_number and search_str in r.serial_number.lower()) or
                            (r.asset_tag and search_str in r.asset_tag.lower()) or
                            (r.pallet_number and search_str in r.pallet_number.lower())
                )
                task.internal_inventory_filtered_ids = filtered_records
            else:
                task.internal_inventory_filtered_ids = task.inventory_line_ids
    
    # Champs pour l'inventaire client
    client_inventory_count = fields.Integer(
        string='Client Inventory Count',
        compute='_compute_client_inventory_count',
        store=False
    )
    
    client_inventory_search = fields.Char(
        string='Search Client Inventory',
        store=False
    )
    
    client_inventory_filtered_ids = fields.One2many(
        'gr.client.inventory',
        'task_id',
        string='Filtered Client Inventory',
        compute='_compute_client_inventory_filtered_ids',
    )
    
    client_inventory_ids = fields.One2many(
        'gr.client.inventory',
        'task_id',
        string='Client Inventory Items'
    )
    
    @api.depends('client_inventory_search', 'client_inventory_ids.serial_number', 
                'client_inventory_ids.asset_tag', 'client_inventory_ids.pallet_number')
    def _compute_client_inventory_filtered_ids(self):
        for task in self:
            if task.client_inventory_search:
                search_str = task.client_inventory_search.lower()
                filtered_records = task.client_inventory_ids.filtered(
                    lambda r: (r.serial_number and search_str in r.serial_number.lower()) or
                            (r.asset_tag and search_str in r.asset_tag.lower()) or
                            (r.pallet_number and search_str in r.pallet_number.lower())
                )
                task.client_inventory_filtered_ids = filtered_records
            else:
                task.client_inventory_filtered_ids = task.client_inventory_ids
    
    @api.depends('client_inventory_ids')
    def _compute_client_inventory_count(self):
        for task in self:
            task.client_inventory_count = len(task.client_inventory_ids)
    
    # Champs pour les écarts
    extra_items_count = fields.Integer(
        string='Extra Items Count',
        compute='_compute_discrepancy_counts',
        store=False
    )
    
    missing_items_count = fields.Integer(
        string='Missing Items Count',
        compute='_compute_discrepancy_counts',
        store=False
    )
    
    discrepancies_ids = fields.One2many(
        'gr.discrepancy',
        'task_id',
        string='Discrepancies'
    )
    
    @api.depends('internal_inventory_filtered_ids')
    def _compute_internal_inventory_count(self):
        for task in self:
            task.internal_inventory_count = len(task.internal_inventory_filtered_ids)
    
    @api.depends('client_inventory_filtered_ids')
    def _compute_client_inventory_count(self):
        for task in self:
            task.client_inventory_count = len(task.client_inventory_filtered_ids)
    
    @api.depends('discrepancies_ids', 'discrepancies_ids.discrepancy_type')
    def _compute_discrepancy_counts(self):
        for task in self:
            task.extra_items_count = self.env['gr.discrepancy'].search_count([
                ('task_id', '=', task.id),
                ('discrepancy_type', '=', 'extra')
            ])
            task.missing_items_count = self.env['gr.discrepancy'].search_count([
                ('task_id', '=', task.id),
                ('discrepancy_type', '=', 'missing')
            ])
            
    @api.constrains('lot_name')
    def _check_lot_name_alphanumeric(self):
        for record in self:
            if record.lot_name:
                # Vérification de la longueur (doit être STRICTEMENT bloquante)
                if len(record.lot_name) > 6:
                    raise ValidationError("ERREUR: Le nom du lot ne doit pas dépasser 6 caractères.")
                
                # Vérification des caractères alphanumériques
                if not re.match(r'^[A-Z0-9]+$', record.lot_name):
                    raise ValidationError("ERREUR: Le nom du lot ne doit contenir que des caractères alphanumériques (A-Z, 0-9).")
                
                # Vérification de l'unicité (Python validation)
                duplicate = self.search([
                    ('lot_name', '=', record.lot_name),
                    ('id', '!=', record.id)
                ])
                if duplicate:
                    raise ValidationError(f"ERREUR: Le nom du lot '{record.lot_name}' existe déjà. Il doit être unique.")

    @api.onchange('lot_name')
    def _onchange_lot_name_uppercase(self):
        if self.lot_name:
            # Convertir en majuscules
            uppercase_value = self.lot_name.upper()
            
            # Vérifier la longueur avant de tronquer
            if len(uppercase_value) > 6:
                # Cela affiche un avertissement visuel à l'utilisateur
                return {
                    'warning': {
                        'title': 'Nom du lot trop long',
                        'message': "Le nom du lot ne doit pas dépasser 6 caractères. Il sera tronqué à l'enregistrement."
                    }
                }
            self.lot_name = uppercase_value

    def write(self, vals):
        if 'lot_name' in vals and vals['lot_name']:
            lot_name_val = vals['lot_name']
            if isinstance(lot_name_val, str) and len(lot_name_val) > 6:
                raise ValidationError("ERREUR: Le nom du lot ne doit pas dépasser 6 caractères.")
            # Gérer les cas où lot_name est explicitement mis à False/None pour l'effacer
            elif lot_name_val is not False and not isinstance(lot_name_val, str):
                raise ValidationError("Format de nom de lot invalide.")
        
        return super(ProjectTask, self).write(vals)

    def action_open_audit_xlsx_wizard(self):
        """
        Open the Audit XLSX Report wizard with the current task's lot name pre-filled.
        """
        self.ensure_one()
        return {
            'name': 'Export Audit XLSX Report',
            'type': 'ir.actions.act_window',
            'res_model': 'audit.report.xlsx.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_lot_name': self.lot_name or '',
            }
        }

    temp_attachment_ids = fields.Many2many(
        'ir.attachment',
        'project_task_attachment_rel',
        'task_id',
        'attachment_id',
        string='Pièces jointes',
        help='Pièces jointes ajoutées lors de la création de la tâche.'
    )

    def action_check_discrepancies(self):
        for task in self:
            if not task.client_inventory_ids:
                raise UserError(_("No client inventory to compare against."))

            task.discrepancies_ids.unlink()

            client_serials = set(task.client_inventory_ids.mapped('serial_number'))
            internal_serials = set(task.inventory_line_ids.mapped('serial_number'))

            missing_serials = client_serials - internal_serials

            for serial in missing_serials:
                client_item = task.client_inventory_ids.filtered(lambda x: x.serial_number == serial)
                if client_item:
                    client_item = client_item[0]
                    asset_tag = client_item.asset_tag or ''
                    pallet_number = client_item.pallet_number or ''
                    client_inventory_id = client_item.id
                else:
                    asset_tag = ''
                    pallet_number = ''
                    client_inventory_id = False

                self.env['gr.discrepancy'].create({
                    'name': f"Missing item with Serial Number: {serial}",
                    'task_id': task.id,
                    'discrepancy_type': 'missing',
                    'serial_number': serial,
                    'asset_tag': asset_tag,
                    'pallet_number': pallet_number,
                    'client_inventory_id': client_inventory_id,
                    'internal_inventory_id': False,
                })

            extra_serials = internal_serials - client_serials

            for serial in extra_serials:
                internal_item = task.inventory_line_ids.filtered(lambda x: x.serial_number == serial)
                if internal_item:
                    internal_item = internal_item[0]
                    asset_tag = internal_item.asset_tag or ''
                    pallet_number = internal_item.pallet_number or ''
                    internal_inventory_id = internal_item.id
                else:
                    asset_tag = ''
                    pallet_number = ''
                    internal_inventory_id = False

                self.env['gr.discrepancy'].create({
                    'name': f"Extra item with Serial Number: {serial}",
                    'task_id': task.id,
                    'discrepancy_type': 'extra',
                    'serial_number': serial,
                    'asset_tag': asset_tag,
                    'pallet_number': pallet_number,
                    'client_inventory_id': False,
                    'internal_inventory_id': internal_inventory_id,
                })

    def action_create_and_open(self):
        """Called by the 'Créer et aller à la tâche' footer button.
        Odoo saves the record before calling this, so the task already exists.
        Returns an act_window that navigates to the full task form.
        """
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'project.task',
            'res_id': self.id,
            'view_mode': 'form',
            'views': [(False, 'form')],
            'target': 'current',
        }

    def _generate_client_hint(self):
        """Generate 3-char client hint.
        Priority: client_destination_name → order_giver_id.name → partner_id.name → 'UNK'
        """
        self.ensure_one()
        import unicodedata

        # Priority order: free-text client name first, then relational fields
        source = (
            self.client_destination_name
            or (self.order_giver_id and self.order_giver_id.name)
            or (self.partner_id and self.partner_id.name)
            or ""
        )

        if source:
            # Remove accents, keep only A-Z 0-9, uppercase, take first 3 chars
            source = unicodedata.normalize('NFKD', source).encode('ASCII', 'ignore').decode('ASCII')
            source = re.sub(r'[^A-Z0-9]', '', source.upper())
            if source:
                return source[:3]

        return "UNK"
    
    def _generate_year_hint(self):
        """Generate 1-char year hint (last digit of current year)."""
        from datetime import datetime
        return str(datetime.now().year)[-1]
    
    def _generate_sequence(self, client_hint, year_hint):
        """Generate 2-char sequence with collision handling."""
        self.ensure_one()
        prefix = f"{client_hint}{year_hint}"
        
        # Find existing lots with same prefix
        existing_lots = self.search([('lot_name', '=like', f"{prefix}%")]).mapped('lot_name')
        
        # Extract sequence numbers (last 2 chars)
        sequences = []
        for lot in existing_lots:
            if len(lot) >= 6 and lot[:4] == prefix:
                try:
                    seq = int(lot[4:6])
                    sequences.append(seq)
                except ValueError:
                    continue
        
        # Find next available sequence
        max_seq = max(sequences) if sequences else 0
        next_seq = max_seq + 1
        
        # Ensure 2-digit format
        return f"{next_seq:02d}"
    
    def _generate_lot_name(self):
        """Generate complete lot name with format: XXXYY (client+year+sequence)."""
        self.ensure_one()
        
        client_hint = self._generate_client_hint()
        year_hint = self._generate_year_hint()
        sequence = self._generate_sequence(client_hint, year_hint)
        
        return f"{client_hint}{year_hint}{sequence}"
    
    def _auto_generate_lot_name_if_empty(self):
        """Auto-generate lot name if empty."""
        if not self.lot_name:
            try:
                generated_name = self._generate_lot_name()
                self.lot_name = generated_name
                _logger.info(f"Auto-generated lot name: {generated_name} for task {self.id}")
            except Exception as e:
                _logger.error(f"Failed to auto-generate lot name for task {self.id}: {str(e)}")
                # Don't raise error, just log it

    @api.model
    def default_get(self, fields_list):
        result = super().default_get(fields_list)
        # When opening the creation form (gr_creation_form context flag),
        # pre-fill date_deadline to today+1 so the form always has a valid deadline.
        # This prevents enterprise's _onchange_planned_dates from wiping planned_date_begin.
        if self.env.context.get('gr_creation_form') and 'date_deadline' in fields_list:
            if not result.get('date_deadline'):
                result['date_deadline'] = fields.Date.today() + timedelta(days=1)
        return result

    @api.model
    def create(self, vals):
        temp_attachments = vals.pop('temp_attachment_ids', False)
        _logger.info(f"Creating task with temp attachments: {temp_attachments}")

        # Sync planned_date_begin from date_deadline when only deadline is provided.
        # The creation form collects date_deadline (avoids enterprise onchange clearing
        # planned_date_begin). Here we mirror it to planned_date_begin at midnight.
        if vals.get('date_deadline') and not vals.get('planned_date_begin'):
            dl = vals['date_deadline']
            if isinstance(dl, str):
                dl = fields.Date.from_string(dl)
            if isinstance(dl, date) and not isinstance(dl, datetime):
                vals['planned_date_begin'] = datetime.combine(dl, dt_time(0, 0, 0))
            elif isinstance(dl, datetime):
                vals['planned_date_begin'] = dl.replace(hour=0, minute=0, second=0, microsecond=0)

        # Auto-generate lot_name if not provided
        if not vals.get('lot_name'):
            # Create task first to get access to related fields
            task = super(ProjectTask, self).create(vals)
            # Then auto-generate lot_name
            task._auto_generate_lot_name_if_empty()
        else:
            task = super(ProjectTask, self).create(vals)

        if temp_attachments:
            for command in temp_attachments:
                if command[0] == 6:
                    attachment_ids = command[2]
                    attachments = self.env['ir.attachment'].browse(attachment_ids)
                    for attachment in attachments:
                        _logger.info(f"Linking attachment {attachment.id} to task {task.id}")
                        attachment.write({
                            'res_model': 'project.task',
                            'res_id': task.id,
                        })
                elif command[0] == 4:
                    attachment_id = command[1]
                    attachment = self.env['ir.attachment'].browse(attachment_id)
                    _logger.info(f"Linking existing attachment {attachment.id} to task {task.id}")
                    attachment.write({
                        'res_model': 'project.task',
                        'res_id': task.id,
                    })
                elif command[0] == 0:
                    attachment_vals = command[2]
                    attachment = self.env['ir.attachment'].create(attachment_vals)
                    _logger.info(f"Linking new attachment {attachment.id} to task {task.id}")
                    attachment.write({
                        'res_model': 'project.task',
                        'res_id': task.id,
                    })
        # --- Aiken lot creation (non-blocking) ---
        if vals.get('create_aiken_lot') and task.lot_name:
            customer = (
                task.client_destination_name
                or (task.order_giver_id and task.order_giver_id.name)
                or (task.partner_id and task.partner_id.name)
                or ''
            )
            try:
                self.env['gr.erasure.service'].create_lot(task.lot_name, customer)
                _logger.info(
                    '[aiken] Lot %s created in Aiken Workbench for task %s.',
                    task.lot_name, task.id,
                )
            except Exception as exc:  # noqa: BLE001 — intentionally non-blocking
                _logger.error(
                    '[aiken] Failed to create lot %s in Aiken Workbench for task %s: %s',
                    task.lot_name, task.id, exc, exc_info=True,
                )
                try:
                    self.env['bus.bus']._sendone(
                        self.env.user.partner_id,
                        'simple_notification',
                        {
                            'title': _('Lot Aiken non créé'),
                            'message': _(
                                'La tâche a été créée, mais le lot %s n\'a pas pu être '
                                'créé dans Aiken Workbench.\nErreur : %s'
                            ) % (task.lot_name, str(exc)),
                            'type': 'warning',
                            'sticky': True,
                        },
                    )
                except Exception as bus_exc:
                    _logger.error('[aiken] Could not send bus notification: %s', bus_exc)
        return task

    # ── RSE tracking fields ──
    rse_total_units = fields.Integer(
        string='Total unités traitées',
        default=0,
        help="Nombre total d'unités traitées dans cette opération"
    )
    rse_reuse_units = fields.Integer(
        string='Unités réemploi',
        default=0,
        help="Nombre d'unités orientées vers le réemploi"
    )
    rse_recycle_units = fields.Integer(
        string='Unités recyclage',
        default=0,
        help="Nombre d'unités orientées vers le recyclage"
    )
    rse_co2_saved_kg = fields.Float(
        string='CO₂ économisé (kg)',
        default=0.0,
        digits=(12, 2),
        help="Kilogrammes de CO₂ économisés grâce à cette opération"
    )

    # ── Deliverable indicators (computed) ──
    has_rapport_rse = fields.Boolean(
        string='Rapport RSE',
        compute='_compute_deliverable_status',
        store=False,
    )
    has_inventaire = fields.Boolean(
        string='Inventaire',
        compute='_compute_deliverable_status',
        store=False,
    )
    has_certificat_audit = fields.Boolean(
        string="Certificat d'audit",
        compute='_compute_deliverable_status',
        store=False,
    )
    has_certificat_effacement = fields.Boolean(
        string="Certificat d'effacement",
        compute='_compute_deliverable_status',
        store=False,
    )

    count_rapport_rse = fields.Integer(
        string='Nb matchs Rapport RSE',
        compute='_compute_deliverable_status',
        store=False,
    )
    count_inventaire = fields.Integer(
        string='Nb matchs Inventaire',
        compute='_compute_deliverable_status',
        store=False,
    )
    count_certificat_audit = fields.Integer(
        string="Nb matchs Certificat d'audit",
        compute='_compute_deliverable_status',
        store=False,
    )
    count_certificat_effacement = fields.Integer(
        string="Nb matchs Certificat d'effacement",
        compute='_compute_deliverable_status',
        store=False,
    )

    @api.depends('document_ids', 'document_ids.tag_ids')
    def _compute_deliverable_status(self):
        """Compute has_* and count_* for each deliverable type."""
        for task in self:
            for slug, config in DELIVERABLE_CONFIG.items():
                field_suffix = slug.replace('-', '_')
                count = self._count_deliverable_matches(task, config)
                setattr(task, f'has_{field_suffix}', count > 0)
                setattr(task, f'count_{field_suffix}', count)

    def _count_deliverable_matches(self, task, config):
        """Count documents/attachments matching a deliverable config.

        Strategy:
          1. Search task.document_ids by tag (priority)
          2. Fallback: ir.attachment regex on filename
        Returns the total candidate count.
        """
        candidates = 0

        # Strategy 1: document_ids by tag
        if hasattr(task, 'document_ids') and task.document_ids:
            for doc in task.document_ids:
                if doc.tag_ids and any(
                    config['tag'].lower() in tag.name.lower()
                    for tag in doc.tag_ids
                ):
                    candidates += 1

        # Strategy 2: fallback ir.attachment regex (only if no tag matches)
        if not candidates:
            attachments = self.env['ir.attachment'].sudo().search([
                ('res_model', '=', 'project.task'),
                ('res_id', '=', task.id),
            ])
            pattern = re.compile(config['regex'], re.IGNORECASE)
            for att in attachments:
                if att.name and pattern.search(att.name):
                    candidates += 1

        return candidates

    # ── Site de traitement ──
    site_id = fields.Many2one(
        'gr.site',
        string='Site GR',
        help='Site de traitement de cette opération.',
        tracking=True,
    )

    # ── Deliverable indicators v2 : tagged-only + warning non-tague ──
    # Surcharge les has_* de v1 (qui incluaient le fallback regex).
    # has_* = True UNIQUEMENT si document avec bon tag (pas fallback seul)
    # untagged_* = True si fichier present par nom mais sans tag -> warning
    has_rapport_rse = fields.Boolean(
        string='Rapport RSE',
        compute='_compute_deliverable_status',
        store=False,
    )
    has_inventaire = fields.Boolean(
        string='Inventaire',
        compute='_compute_deliverable_status',
        store=False,
    )
    has_certificat_audit = fields.Boolean(
        string="Certificat d'audit",
        compute='_compute_deliverable_status',
        store=False,
    )
    has_certificat_effacement = fields.Boolean(
        string="Certificat d'effacement",
        compute='_compute_deliverable_status',
        store=False,
    )
    untagged_rapport_rse = fields.Boolean(
        string='Rapport RSE non tague',
        compute='_compute_deliverable_status',
        store=False,
    )
    untagged_inventaire = fields.Boolean(
        string='Inventaire non tague',
        compute='_compute_deliverable_status',
        store=False,
    )
    untagged_certificat_audit = fields.Boolean(
        string="Certificat d'audit non tague",
        compute='_compute_deliverable_status',
        store=False,
    )
    untagged_certificat_effacement = fields.Boolean(
        string="Certificat d'effacement non tague",
        compute='_compute_deliverable_status',
        store=False,
    )

    def _count_deliverable_tagged(self, task, config):
        """Count documents with the correct tag (STRICT — no fallback regex).
        Returns count of tag-matched documents only.
        Un fichier sans tag ne compte PAS, meme si son nom matche le regex.
        """
        if not hasattr(task, 'document_ids') or not task.document_ids:
            return 0
        candidates = 0
        for doc in task.document_ids:
            if doc.tag_ids and any(
                config['tag'].lower() in tag.name.lower()
                for tag in doc.tag_ids
            ):
                candidates += 1
        return candidates

    def _count_deliverable_fallback(self, task, config):
        """Count attachments matching by filename regex (no tag check).
        Used to detect 'present but not tagged' (warning state).
        Ne rentre en jeu QUE si aucun doc tague n'est trouve.
        """
        attachments = self.env['ir.attachment'].sudo().search([
            ('res_model', '=', 'project.task'),
            ('res_id', '=', task.id),
        ])
        pattern = re.compile(config['regex'], re.IGNORECASE)
        candidates = 0
        for att in attachments:
            if att.name and pattern.search(att.name):
                candidates += 1
        return candidates

    @api.depends('document_ids', 'document_ids.tag_ids')
    def _compute_deliverable_status(self):
        """Compute has_*, count_*, untagged_* — version corrigee.

        Semantique :
          has_*      = True si document AVEC le bon tag (STRICT, sans fallback)
          count_*    = nombre de documents avec le bon tag
          untagged_* = True si fichier present par nom (regex) mais SANS tag correct
                       -> affiche un warning cote UI, pas une coche verte

        Surcharge la v1 qui confondait tagged et fallback dans has_*.
        Python utilise la derniere definition dans la classe.
        """
        for task in self:
            for slug, config in DELIVERABLE_CONFIG.items():
                field_suffix = slug.replace('-', '_')
                tagged = self._count_deliverable_tagged(task, config)
                fallback = self._count_deliverable_fallback(task, config) if not tagged else 0
                setattr(task, f'has_{field_suffix}', tagged > 0)
                setattr(task, f'count_{field_suffix}', tagged)
                setattr(task, f'untagged_{field_suffix}', tagged == 0 and fallback > 0)





    # ── Documents folder (dédié par tâche) ──
    # Override du related standard de documents_project : chaque tâche a son propre
    # sous-dossier au lieu d'hériter du dossier du projet. Sans ce override, toutes
    # les tâches d'un projet partagent le même dossier et le panneau gauche ne
    # filtre pas correctement.
    documents_folder_id = fields.Many2one(
        'documents.folder',
        string='Task Documents Folder',
        related=False,
    )

    shared_document_ids = fields.One2many(
        'documents.document',
        compute='_compute_shared_document_ids',
        string='Shared Documents',
        help='Documents visibles dans le portail client',
    )

    @api.depends('document_ids')
    def _compute_shared_document_ids(self):
        """Rend tous les documents de la tâche visibles en portail."""
        for task in self:
            task.shared_document_ids = task.document_ids

    def action_view_documents_project_task(self):
        """Override : initialise le dossier de la tâche avant d'ouvrir les Documents."""
        if not self.documents_folder_id:
            self._init_documents_folder()
        return super().action_view_documents_project_task()

    def _get_document_folder(self):
        """Retourne le dossier de la tâche, en le créant si nécessaire."""
        return self.documents_folder_id or self._init_documents_folder()

    def _init_documents_folder(self):
        """Crée un sous-dossier dédié à cette tâche dans les Documents."""
        folder = self.env['documents.folder'].create(self._prepare_documents_folder())
        self.documents_folder_id = folder.id
        return folder

    def _prepare_documents_folder(self):
        """Valeurs pour créer le dossier de la tâche.

        Le dossier parent est celui du projet. Si le projet n'a pas encore de
        dossier, on utilise le dossier racine Projets de documents_project.
        """
        parent_folder_id = (
            self.project_id.documents_folder_id.id
            if self.project_id and self.project_id.documents_folder_id
            else self.env.ref('documents_project.documents_project_folder').id
        )
        return {
            'name': self.name,
            'parent_folder_id': parent_folder_id,
            'task_ids': [fields.Command.link(self.id)],
        }


class GrSite(models.Model):
    _name = 'gr.site'
    _description = 'Site GR'

    name = fields.Char(string='Nom', required=True)
    address = fields.Text(string='Adresse')
    partner_id = fields.Many2one('res.partner', string='Contact site')
    active = fields.Boolean(default=True)

    _sql_constraints = [
        ('name_unique', 'UNIQUE(name)', 'Le nom du site doit être unique.')
    ]
