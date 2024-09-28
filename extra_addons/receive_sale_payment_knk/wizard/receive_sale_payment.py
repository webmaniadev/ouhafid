# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import UserError


TYPES = [('check', 'Check'),
         ('effect', 'Effect'),
         ('transfer_payment', 'Transfer / Payment')]

class SalePaymentConfirm(models.Model):
    _name = 'receive.sale.payment'
    _description = 'Sale Payment'

    operation_type = fields.Selection(TYPES, string="Operation Type")
    operation_number = fields.Char(string="Operation Number")
    operation_date = fields.Date(string="Operation Date")
    partner_id = fields.Many2one('res.partner', string="Customer")
    amount = fields.Float(string="Amount")
    ref = fields.Char(string='Memo', copy=False)
    journal_id = fields.Many2one('account.journal', string="Journal",  domain="[('type', 'in', ('bank', 'cash'))]")
    journal_type = fields.Selection(related='journal_id.type', string="Type")
    date = fields.Date(string="Payment Date", required=True, default=fields.Date.context_today)
    currency_id = fields.Many2one('res.currency', string='Currency')

    def sale_payment_confirm(self):
        if not self.amount:
            raise UserError(_('You must set Amount!'))
        sale = self.env['sale.order'].browse(self.env.context.get('active_id'))
        values = {
            'date': self.date,
            'ref': self.ref,
            'partner_id': sale.partner_id.id,
            'partner_type': 'customer',
            'amount': self.amount,
            'journal_id': self.journal_id.id,
            'operation_type': self.operation_type,
            'operation_number': self.operation_number or '',
            'operation_date': self.operation_date,
            'sale_id': self.env.context.get('active_id'),
        }
        return self.env['account.payment'].create(values)

