from odoo import http
from odoo.http import request


class CustomSignupRequest(http.Controller):

    @http.route(['/greenremarket/signup'], type='http', auth='public', website=True)
    def signup_form(self, **kw):
        return request.render('grm_website.signup_form')

    @http.route(['/greenremarket/signup/submit'], type='http', auth='public', website=True, csrf=True)
    def signup_form_submit(self, **post):
        partner_vals = {
            'name': post.get('name'),
            'email': post.get('email'),
            'phone': post.get('phone'),
            'function': post.get('function'),
            'company_name': post.get('company_name'),
            'street': post.get('street'),
            'zip': post.get('zip'),
            'city': post.get('city'),
            'country_id': int(post.get('country_id')) if post.get('country_id') else False,
            'comment': "Demande d'accès via formulaire d'inscription public",
        }

        request.env['res.partner'].sudo().create(partner_vals)

        return request.render('grm_website.signup_thank_you')
