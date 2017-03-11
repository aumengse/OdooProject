# -*- coding: utf-8 -*-
from openerp import http

# class PaymentReseller(http.Controller):
#     @http.route('/payment_reseller/payment_reseller/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/payment_reseller/payment_reseller/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('payment_reseller.listing', {
#             'root': '/payment_reseller/payment_reseller',
#             'objects': http.request.env['payment_reseller.payment_reseller'].search([]),
#         })

#     @http.route('/payment_reseller/payment_reseller/objects/<model("payment_reseller.payment_reseller"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('payment_reseller.object', {
#             'object': obj
#         })