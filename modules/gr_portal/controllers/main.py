# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request


class GRPortalHome(http.Controller):
    """
    Overrides the website home route (/) to prevent unauthenticated users
    from landing on the grm_website marketing page.

    Routing priority:
      - Not authenticated  → /web/login
      - Portal user        → /my  (their portal dashboard)
      - Internal user      → /odoo (the Odoo backend)

    This keeps the grm_website landing page entirely out of the user flow.
    Website editors can still access pages directly via their backend links.
    """

    @http.route('/', type='http', auth='public', website=True, sitemap=False)
    def home(self, **kw):
        if request.env.user._is_public():
            # Not logged in → send to the branded login page
            return request.redirect('/web/login')
        if request.env.user.has_group('base.group_portal'):
            # Portal client → their dashboard
            return request.redirect('/my')
        # Internal / admin user → Odoo backend
        return request.redirect('/odoo')
