# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
################################################################################

from odoo import models, fields, api, _
import odoo.addons.decimal_precision as dp

class account_invoice_line(models.Model):

    _inherit = "account.invoice.line"


    @api.one
    @api.depends('product_id')
    def _get_product_cost(self):
        for n in self:
            frm_cur = self.env.user.company_id.currency_id
            to_cur = n.invoice_id.currency_id
            purchase_price = n.product_id.standard_price
            if n.uom_id != n.product_id.uom_id:
                purchase_price = n.product_id.uom_id._compute_price(purchase_price, n.uom_id)            
            price = frm_cur._convert(
                                    purchase_price, to_cur,
                                    n.company_id or self.env.user.company_id,
                                    fields.Date.today(), round=False)
            n.purchase_price =  price

    
    @api.one
    @api.depends('price_unit', 'discount', 'invoice_line_tax_ids', 'quantity',
        'product_id', 'invoice_id.partner_id', 'invoice_id.currency_id')
    def _calc_margin(self):
        line_mrg_tot = 0
        cmp = 0.0
        cmp = (self.purchase_price * self.quantity)
        margin = self.price_subtotal - cmp
        margin_subtotal_signed = self.invoice_id.currency_id.with_context(date=self.invoice_id.date_invoice).compute(margin, self.invoice_id.company_id.currency_id)
        sign = self.invoice_id.type in ['in_refund', 'out_refund'] and -1 or 1
        self.margin_subtotal_signed = margin_subtotal_signed * sign
        self.line_margin = margin

    @api.onchange('product_id')
    def _onchange_product_id(self):
        res = super(account_invoice_line, self)._onchange_product_id()
        if self.product_id:
            frm_cur = self.env.user.company_id.currency_id
            to_cur = self.invoice_id.currency_id
            purchase_price = self.product_id.standard_price
            if self.uom_id != self.product_id.uom_id:
                purchase_price = self.product_id.uom_id._compute_price(purchase_price, self.uom_id)
            price = frm_cur._convert(
                                    purchase_price, to_cur,
                                    self.invoice_id.company_id or self.env.user.company_id,
                                    fields.Date.today(), round=False)   
            self.purchase_price = price
            
        return res

    purchase_price =  fields.Float('Cost', compute='_get_product_cost' ,digits_compute= dp.get_precision('Product Price'))
    margin_subtotal_signed = fields.Float(string='Margin Signed', currency_field='company_currency_id',
        readonly=True,store=True, compute='_calc_margin')
    line_margin = fields.Float(string='Margin', digits= dp.get_precision('Account'),store=True, readonly=True, compute='_calc_margin')


class account_invoice(models.Model):
    _inherit = "account.invoice"

    margin_cust = fields.Float('Margin %', compute='_calc_margin')
    margin_calc = fields.Float('Margin', compute='_calc_margin')
    
    @api.multi
    def _calc_margin(self):
        line_mrg_tot = 0
        for order in self:
            margin_per = 0.0
            margin = 0.0
            cmp = 0.0
            for line in order.invoice_line_ids:
                cmp = 0
                cmp += (line.purchase_price * line.quantity)
                margin = line.price_subtotal - cmp
                #line.line_margin = margin
                line_mrg_tot += margin 
        if order.amount_total != 0.0 and order.amount_untaxed != 0.0:
                order.update({
                    'margin_cust' : (line_mrg_tot * 100) / order.amount_untaxed,
                    'margin_calc' : line_mrg_tot
                })

