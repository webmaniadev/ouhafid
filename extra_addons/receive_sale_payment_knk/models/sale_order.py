# -*- coding: utf-8 -*-
# Powered by Kanak Infosystems LLP.
# © 2020 Kanak Infosystems LLP. (<https://www.kanakinfosystems.com>)

from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    sale_payment_ids = fields.One2many('account.payment', 'sale_id', string='Payment')
    payment_amt = fields.Float(string="Payment Amount", compute='_get_payment_amount')
    remain_paid = fields.Float(string="Remain paid", compute='_get_payment_amount')

    def _get_payment_count(self):
        for record in self:
            record.payment_count = len(record.sale_payment_ids)

    def action_view_payments(self):
        action = self.env.ref('receive_sale_payment_knk.action_account_payments').read([])[0]
        payments = self.env['account.payment'].search([('sale_id', '=', self.id)])
        action.update({
            'domain': [('id', 'in', payments.ids)],
            'context': {'do_not_unlink_payment': True}
        })
        return action

    @api.depends('sale_payment_ids', 'sale_payment_ids.amount', 'amount_total')
    def _get_payment_amount(self):
        for record in self:
            payment_amt = sum([ac.amount for ac in record.sale_payment_ids.filtered(lambda l: l.state != 'cancel')])
            record.payment_amt = payment_amt
            record.remain_paid = record.amount_total - payment_amt
