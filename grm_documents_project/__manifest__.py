{
    "name": "GRM - Documents Project",
    "version": "17.0.1.1.2",
    "category": "Services/Project",
    "sequence": 45,
    "summary": "Flag delivrable documents",
    "depends": [
        "documents_project",
        "grm_website",
    ],
    "data": [
        "data/documents_facet_data.xml",
        "data/documents_tag_data.xml",
        "templates/project_portal_project_task_templates.xml",
        "templates/portal_task_documents.xml",
    ],
    "installable": True,
    "assets": {
        "web.assets_frontend": [
            "grm_documents_project/static/src/**/*",
        ],
    },
    "application": False,
    "license": "LGPL-3",
}
