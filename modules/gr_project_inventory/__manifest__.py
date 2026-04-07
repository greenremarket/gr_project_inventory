# -*- coding: utf-8 -*-
{
    'name': 'Green Remarket Project Inventory',
    'version': '17.0.4.1.0',
    'category': 'Project',
    'summary': 'RSE tracking, site management, document links, and deliverable indicators on project tasks',
    'description': """
Green Remarket Project Inventory v4.0
======================================
Consolidated backend module. Absorbed grm_documents_project.

Features:
- RSE tracking fields (total units, reuse, recycle, CO₂)
- Deliverable indicators (has_*/count_* computed from document tags)
- gr.site, gr.chassis, gr.observation models
- Document management (folders, documents linking — stubs, sync from target)
- Deliverable download routes (stubs, sync from target)
    """,
    'author': 'Morad IGMIR',
    'website': 'https://greenremarket.fr',
    'depends': [
        'project', 'project_enterprise', 'documents', 'documents_project',
        'barcodes', 'report_xlsx', 'report_xlsx_helper',
    ],
    'data': [
        # Security
        'security/gr_groups.xml',
        'security/ir.model.access.csv',
        'security/gr_rules.xml',
        # Reference data (CRITIQUE : référencés par des données de production)
        'data/product_type_data.xml',
        'data/chassis_data.xml',
        'data/manufacturer_data.xml',
        'data/deliverable_data.xml',
        'data/barcode_nomenclature.xml',
        'data/barcode_data.xml',
        'data/ir_sequence_data.xml',
        'data/ir_config_parameter.xml',
        # Livrables documents (absorbé depuis grm_documents_project)
        'data/documents_facet_data.xml',
        'data/documents_tag_data.xml',
        # Vues héritées existantes
        'views/views.xml',
        'views/res_config_settings_view.xml',
        'views/audit_report_xlsx_wizard_view.xml',
        'views/task_erasure_button.xml',
        # Rapports (PDF + XLSX via OCA report_xlsx)
        'reports/discrepancy_report.xml',
        'reports/internal_inventory_report.xml',
        'reports/paperformat_erasure.xml',
        'reports/report_action.xml',
        'reports/erasure_certificate.xml',
        # Nouvelles vues RSE/sites (source de vérité = Lovable)
        'views/gr_site_views.xml',
        'views/project_task_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
