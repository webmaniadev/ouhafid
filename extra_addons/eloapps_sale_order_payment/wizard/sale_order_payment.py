from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import datetime
import logging as log

class SaleOrderPayment(models.TransientModel):
    _name = "sale.order.payment"
    _description = "Paiement sur devis"

    company_id = fields.Many2one('res.company','Société', default=lambda self: self.env.company)
    company_currency_id = fields.Many2one(related='company_id.currency_id', string='Company Currency',
        readonly=True, store=True,
        help='Utility field to express amount currency')
    order_id = fields.Many2one('sale.order')
    payment_amount = fields.Monetary(string='montant', currency_field="company_currency_id")

    def _default_journal_id(self):
        return self.env['account.journal'].search([('type','=', 'bank')],limit=1)

    journal_id = fields.Many2one('account.journal', "Journal" ,default=_default_journal_id, domain="[('type', 'in', ['bank','cash'])]",)
    payment_date = fields.Date('Date', default=fields.Date.context_today)
    memo = fields.Char('Mémo')

    def payment_validate(self):

        data = {
        'payment_type': 'inbound',
        'partner_id': self.order_id.partner_id.id,
        'amount' : self.payment_amount,
        'date': self.payment_date,
        'invoice_origin': self.order_id.move_id.name,
        'ref': self.memo,
        'journal_id': self.journal_id.id,
        }

        pay = self.env['account.payment'].create(data)
        pay.action_post()

        pay_lines = pay.move_id.line_ids.filtered(lambda r: not r.reconciled and r.account_id.internal_type == 'receivable')

        sale_lines = self.order_id.move_id.line_ids.filtered(lambda r: not r.reconciled and r.account_id.internal_type == 'receivable')

        lines = pay_lines + sale_lines
        lines.reconcile()
