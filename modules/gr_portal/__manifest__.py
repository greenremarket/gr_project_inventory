# -*- coding: utf-8 -*-
{
    'name': 'Green Remarket — Portal Login',
    'version': '17.0.1.0.0',
    'category': 'Website',
    'summary': 'Video-background login page for Green Remarket',
    'description': """
Green Remarket Portal Login
===========================
Replaces the grm_website CSS-grid login layout with a full-screen video
background, hero section, and image collage.

Inheritance chain:
  website.login_layout (core)
    └─ grm_website.template_login_inherit  (priority 99 — CSS grid)
       └─ gr_portal.gr_login_layout        (priority 100 — video + hero)

  web.login (core form)
    └─ grm_website.template_login_eye      (priority 99 — password eye)
       └─ gr_portal.gr_login_form          (priority 100 — pill inputs + forgot)
    """,
    'author': 'Morad IGMIR / Green Remarket',
    'website': 'https://greenremarket.fr',
    'depends': ['web', 'grm_website'],
    'data': [
        'views/login_templates.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'gr_portal/static/src/css/portal.css',
            'gr_portal/static/src/js/login.js',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
