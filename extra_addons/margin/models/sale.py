# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
################################################################################

from odoo import models, fields, api, _
import odoo.addons.decimal_precision as dp

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"
    
    @api.one
    @api.depends('price_unit','product_uom_qty','tax_id','product_id','order_id.partner_id','order_id.currency_id')
    def _calc_margin(self):
        line_mrg_tot = 0
        cmp = 0.0
        cmp = (self.purchase_price * self.product_uom_qty)
        margin = self.price_subtotal - cmp
        self.line_margin = margin
    
    line_margin = fields.Float(string='Margin', digits= dp.get_precision('Account'),
        store=True, readonly=True, compute='_calc_margin')

    @api.multi
    def _prepare_invoice_line(self, qty):
        res = super(SaleOrderLine, self)._prepare_invoice_line(qty)
        res.update({'purchase_price':self.purchase_price})
        return res

    
class sale_order(models.Model):
    _inherit = "sale.order"

    @api.multi
    def _calc_margin(self):
        for order in self:
            margin_per = 0.0
            margin = 0.0
            cmp = 0.0
            for line in order.order_line:
                cmp += (line.purchase_price * line.product_uom_qty)
#                margin =  order.amount_total - ((line.purchase_price or line.product_id.standard_price) * line.product_uom_qty)
#                margin_per = (line.price_unit -line.purchase_price )/line.price_unit * 100
            if order.amount_total != 0:
                margin = order.amount_untaxed - cmp
                order.update({
                    'margin_cust' : (margin * 100) / order.amount_untaxed,
                    'margin_calc' : order.amount_untaxed - cmp
                })
            else:
                order.update({
                    'margin_cust' : 0.0,
                    'margin_calc' : 0.0
                })

    
    margin_cust = fields.Float('Margin %', compute='_calc_margin' , readonly=True)
    margin_calc = fields.Float('Margin', compute='_calc_margin' , readonly=True)
    
