# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
################################################################################


from odoo import models, fields, api, _
import openerp.addons.decimal_precision as dp


class product_product(models.Model):
    _inherit = "product.template"

    
    def _calc_margin(self):
        for product in self:
            ans = 0
            if product.list_price == 0 or product.standard_price == 0:
                ans = 0
            else:
                ans = ((product.list_price - product.standard_price) / product.list_price) * 100
            product.update({'margin' : ans})                      
                           
    margin = fields.Float('Margin %', compute='_calc_margin' , readonly=True)
    
    list_price = fields.Float('Sale Price', digits_compute=dp.get_precision('Product Price'), help="Base price to compute the customer price. Sometimes called the catalog price.")
    
    standard_price = fields.Float(digits_compute=dp.get_precision('Product Price'),groups="base.group_user", string="Cost Price")
