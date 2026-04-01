# -*- coding: utf-8 -*-
{
    'name': 'Green Remarket — Portal',
    'version': '17.0.1.1.0',
    'category': 'Website',
    'summary': 'Video-background login page and portal home banner for Green Remarket',
    'description': """
Green Remarket Portal
=====================
Login page:
  Replaces the grm_website CSS-grid login layout with a full-screen video
  background, GR logo hero, and glassmorphism form card.

Portal home:
  Adds a branded welcome banner above grm_website’s portal home content.

Inheritance chains:
  website.login_layout
    └─ grm_website.template_login_inherit  (priority 99 — CSS grid)
       └─ gr_portal.gr_login_layout        (priority 100 — video + hero)

  web.login
    └─ grm_website.template_login_eye      (priority 99 — password eye)
       └─ gr_portal.gr_login_form          (priority 100 — pill inputs + forgot)

  grm_website.portal_my_home_custom
    └─ gr_portal.gr_portal_my_home         (priority 20 — welcome banner)
    """,
    'author': 'Morad IGMIR / Green Remarket',
    'website': 'https://greenremarket.fr',
    'depends': ['web', 'portal', 'grm_website'],
    'data': [
        'views/portal_templates.xml',
        'views/login_templates.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'gr_portal/static/src/css/portal.css',
            'gr_portal/static/src/js/portal.js',
            'gr_portal/static/src/js/login.js',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
