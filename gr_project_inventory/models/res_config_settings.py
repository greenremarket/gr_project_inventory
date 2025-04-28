from odoo import models, fields

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    module_gr_project_inventory = fields.Boolean(
        string="Project Inventory Module",
        help="Enable functionalities from the Project Inventory module."
    )

    printer_ip = fields.Char(string="Zebra Printer IP Address", config_parameter='gr_project_inventory.printer_ip', default='192.168.21.43')
    printer_port = fields.Integer(string="Zebra Printer Port", config_parameter='gr_project_inventory.printer_port', default='9100')