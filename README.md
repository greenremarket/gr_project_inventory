# Green Remarket Project Inventory

This Odoo addon provides comprehensive inventory management features for Green Remarket's internal operations. It enables efficient tracking, management, and reporting of inventory items with specific focus on refurbishment and asset management.

## Features

- Internal inventory management with asset tracking
- Client inventory integration
- Barcode scanning support
- Advanced search and filtering capabilities
- Excel report generation
- Multi-item operations support
- Status tracking (NEW, REFURB, NEW-OPEN-BOX, TBD)
- Observation management
- Product categorization (manufacturer, product type, chassis)

## Installation

1. Clone this repository into your Odoo addons directory:
```bash
git clone https://github.com/greenremarket/gr_project_inventory.git
```

2. Add the module path to your Odoo configuration file or start Odoo with the appropriate addons path.

3. Update the Odoo apps list and install the module:
   - Go to Apps
   - Click "Update Apps List"
   - Search for "Green Remarket Project Inventory"
   - Click Install

## Configuration

After installation:

1. Go to Settings > Technical > Security > Access Rights
2. Configure user access rights for the module
3. Set up default values in the configuration settings

## Usage

The module provides the following main features:

- Internal Inventory Management
- Client Inventory Integration
- Asset Tracking
- Reporting
- Multi-item Operations

For detailed usage instructions, please refer to the documentation in the `doc` folder.

## Dependencies

- Odoo 16.0
- Python 3.8+
- XlsxWriter (for Excel report generation)

## Support

For support and issues, please create an issue in the GitHub repository or contact the Green Remarket support team.

## License

This module is proprietary and confidential. All rights reserved. 