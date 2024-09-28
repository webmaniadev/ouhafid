# -*- coding: utf-8 -*-
# from odoo import http


# class MinimumPrice(http.Controller):
#     @http.route('/minimum_price/minimum_price/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/minimum_price/minimum_price/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('minimum_price.listing', {
#             'root': '/minimum_price/minimum_price',
#             'objects': http.request.env['minimum_price.minimum_price'].search([]),
#         })

#     @http.route('/minimum_price/minimum_price/objects/<model("minimum_price.minimum_price"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('minimum_price.object', {
#             'object': obj
#         })
