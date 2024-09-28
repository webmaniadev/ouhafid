# -*- coding: utf-8 -*-
# from odoo import http


# class ModifyBl(http.Controller):
#     @http.route('/modify_bl/modify_bl/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/modify_bl/modify_bl/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('modify_bl.listing', {
#             'root': '/modify_bl/modify_bl',
#             'objects': http.request.env['modify_bl.modify_bl'].search([]),
#         })

#     @http.route('/modify_bl/modify_bl/objects/<model("modify_bl.modify_bl"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('modify_bl.object', {
#             'object': obj
#         })
