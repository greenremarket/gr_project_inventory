# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.addons.web.controllers.home import Home as WebHome
from odoo.addons.website.controllers.main import Website as WebsiteMain
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
        # Werkzeug builds the Location header using the internal request scheme
        # (always http when behind nginx), ignoring X-Forwarded-Proto.
        # This produces "Location: http://..." which modern browsers block as
        # an HTTPS→HTTP downgrade. Read the forwarded proto explicitly.
        environ = request.httprequest.environ
        scheme = environ.get('HTTP_X_FORWARDED_PROTO') or request.httprequest.scheme
        host   = request.httprequest.host

        def url(path):
            return f'{scheme}://{host}{path}'

        if request.env.user._is_public():
            return request.redirect(url('/web/login'), local=False)
        if request.env.user.has_group('base.group_portal'):
            return request.redirect(url('/my'), local=False)
        # Internal / admin users:
        #   - Website editor loads / with ?enable_editor=1 (added by /website/force/1)
        #     → pass through so the editor iframe shows the site correctly.
        #   - Direct browser visit (no enable_editor)
        #     → redirect to the Odoo backend.
        if 'enable_editor' in request.httprequest.args:
            return WebsiteMain().index(**kw)
        return request.redirect(url('/my/home'), local=False)


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
