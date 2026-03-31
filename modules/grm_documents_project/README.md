# grm_documents_project

This Odoo module provides functionality for downloading deliverable documents associated with project tasks as ZIP archives.

## Features

- Adds an HTTP endpoint `/delivrable/download` for authenticated users to download deliverables for selected project tasks.
- Ensures access rights and rules are respected before allowing downloads.
- Returns ZIP files containing the requested deliverable documents.

## Usage

Send a POST request to `/delivrable/download` with a comma-separated list of task IDs:

```
POST /delivrable/download
task_ids=1,2,3
```

The response will be a ZIP file containing the deliverable documents for the specified tasks.

## How to Set a Document as a Deliverable

To mark a document as a deliverable:

1. Go to the **Documents** app in Odoo.
2. Open the document you want to set as a deliverable.
3. In the document’s detail view, locate the **Tags** field.
4. Add the tag **Deliverable** (technical name: `documents_project_delivrable`).
   - If the tag does not exist, your module should create it automatically when installed.
5. Save the document.

Documents with this tag will be recognized as deliverables by the module and included in ZIP

## Installation

1. Place the `grm_documents_project` directory in your Odoo addons path.
2. Update the Odoo app list and install the module from the Apps menu.

## Author

Mickael Arc-Ange ANDRIAMANDIMBINIAINA <kaelmika5@gmail.com>