from odoo import http
from odoo.http import request


class PortalHomeCustom(http.Controller):

    @http.route(['/my/home', '/my'], type='http', auth='user', website=True)
    def my_home(self, **kw):

        user = request.env.user
        partner = user.partner_id

        invoices = request.env['account.move'].sudo().search([
            ('move_type', 'in', ('out_invoice', 'out_refund')),
            ('message_partner_ids', 'in', [partner.id]),
        ], limit=5)
        # Search tasks the user can see in the portal:
        # - portal-visible project
        # - tagged PD3E (matches template filter, avoids fetching invisible tasks)
        # - user follows the project, follows the task, or is assigned
        commercial_partner_id = partner.commercial_partner_id.id
        tasks = request.env['project.task'].sudo().search([
            ('project_id.privacy_visibility', '=', 'portal'),
            ('active', '=', True),
            ('tag_ids.name', 'like', 'PD3E'),
            '|', '|',
            ('project_id.message_partner_ids', 'child_of', [commercial_partner_id]),
            ('message_partner_ids', 'child_of', [commercial_partner_id]),
            ('user_ids', 'in', [user.id]),
        ], limit=10, order='write_date desc')
        quotes_count = request.env['sale.order'].sudo().search_count([
            ('state', 'in', ['sent']),
            ('partner_id', '=', partner.id)
        ])

        sign_request_count = request.env['sign.request.item'].sudo().search_count([
            ('partner_id', '=', partner.id),
            ('state', '=', 'sent')
        ])

        return request.render('grm_website.portal_my_home_custom', {
            'invoices': invoices,
            'tasks': tasks,
            'user': user,
            'quotes_count': quotes_count,
            'sign_request_count': sign_request_count,
        })
