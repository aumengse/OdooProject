# -*- coding: utf-8 -*-
from openerp import http

# class PaymentResellerData(http.Controller):
#     @http.route('/payment_reseller_data/payment_reseller_data/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/payment_reseller_data/payment_reseller_data/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('payment_reseller_data.listing', {
#             'root': '/payment_reseller_data/payment_reseller_data',
#             'objects': http.request.env['payment_reseller_data.payment_reseller_data'].search([]),
#         })

#     @http.route('/payment_reseller_data/payment_reseller_data/objects/<model("payment_reseller_data.payment_reseller_data"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('payment_reseller_data.object', {
#             'object': obj
#         })