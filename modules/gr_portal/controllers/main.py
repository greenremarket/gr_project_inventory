# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.addons.web.controllers.home import Home as WebHome
try:
    from odoo.addons.web.controllers.utils import is_user_internal
except ImportError:
    # Fallback for older Odoo 17.0 builds that don't have this helper
    def is_user_internal(uid):
        return request.env['res.users'].browse(uid).has_group('base.group_user')


class GRPortalHome(http.Controller):
    """
    Overrides the website home route (/) to prevent any user from landing
    on the grm_website marketing page.

    Routing:
      - Not authenticated  → /web/login  (branded login page)
      - Portal user        → /my         (portal dashboard)
      - Internal user      → /web        (Odoo backend — /web is stable across
                                          all 17.0 builds; /odoo may not exist)
    """

    @http.route('/', type='http', auth='public', website=True, sitemap=False)
    def home(self, **kw):
        if request.env.user._is_public():
            return request.redirect('/web/login')
        if request.env.user.has_group('base.group_portal'):
            return request.redirect('/my')
        # Internal / admin user → backend (avoid /odoo which may not exist
        # as a registered route in all 17.0 builds and falls to website 404)
        return request.redirect('/web')


class GRPortalLogin(WebHome):
    """
    Overrides _login_redirect so that after a successful login:
      - Portal users land on /my (their dashboard) instead of /
      - Internal users go to /web (backend) as normal
      - Any explicit ?redirect= parameter is always honoured first

    Pattern recommended by Odoo 17 community for portal login redirection.
    """

    @http.route()
    def web_login(self, redirect=None, *args, **kw):
        return super().web_login(redirect=redirect, *args, **kw)

    def _login_redirect(self, uid, redirect=None):
        if redirect:
            return redirect
        if not is_user_internal(uid):
            # Portal / public user → portal dashboard
            return '/my'
        # Internal user → standard backend
        return super()._login_redirect(uid, redirect=redirect)
