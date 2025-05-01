# __manifest__.py

{
    'name': 'Green Remarket Project Inventory Management',
    'version': '1.2',
    'category': 'Inventory',
    'summary': 'Manage client and internal inventories within project tasks and track discrepancies.',
    'description': """
        This module allows you to manage client-provided inventories and internal inventories within project tasks. It provides functionality to check for discrepancies between the client and internal inventories, identifying missing and extra items.
    """,
    'author': 'Morad Igmir',
    'company': 'Green Remarket',
    'website': 'https://greenremarket.fr/',
    'depends': ['base', 'project', 'report_xlsx', 'report_xlsx_helper', 'stock', 'barcodes'],
    'data': [
        'security/ir.model.access.csv',
        'reports/discrepancy_report.xml',
        'reports/internal_inventory_report.xml',
        'views/views.xml',
        'views/res_config_settings_view.xml',
        'data/product_type_data.xml',
        'data/chassis_data.xml',
        'data/deliverable_data.xml',
        'data/manufacturer_data.xml',
        'data/barcode_nomenclature.xml',
        # Erasure certificate feature additions:
        'data/ir_config_parameter.xml',
        'views/task_erasure_button.xml',
        'reports/paperformat_erasure.xml',
        'reports/report_action.xml',
        'reports/erasure_certificate.xml',
    ],
    'qweb': [
        'reports/erasure_certificate.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
    'external_dependencies': {
        'python': ['pymysql>=1.1'],
    },
}
