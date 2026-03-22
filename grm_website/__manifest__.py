{
    'name': 'Greenremarket Website theme',
    'description': 'Greenremarket Website theme',
    'category': 'Website/Theme',
    'version': '17.0.1.1.3',
    'author': 'Greenremarket',
    'license': 'LGPL-3',
    'depends': ['website', 'sale_project', 'sign', 'contacts'],
    'data': [
        # DATA
        'data/project_tags.xml',
        
        # PAGES
        'data/pages/home_page.xml',
        'data/pages/contact_us.xml',

        # TEMPLATES
        'templates/layout.xml',
        'templates/login.xml',
        'templates/my_account.xml',
        'templates/signup.xml',
        'templates/operations.xml',

        # VIEWS
        'views/res_partner_views.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'grm_website/static/src/scss/layout_custom.scss',
            'grm_website/static/src/scss/fonts.scss',
            'grm_website/static/src/scss/login.scss',
            'grm_website/static/src/scss/my_account.scss',
            'grm_website/static/src/scss/responsive.scss',
            'grm_website/static/src/js/validation_field.js',
            'grm_website/static/src/js/task_short.js',
            'grm_website/static/src/js/loader.js',
        ],
        "web._assets_primary_variables": [
            'grm_website/static/src/scss/primary_variables.scss',
        ],
        "web._assets_bootstrap_frontend": [
            ("prepend", "grm_website/static/src/scss/bootstrap_overridden.scss"),
        ],
    },
    'installable': True,
    'application': True,
}
