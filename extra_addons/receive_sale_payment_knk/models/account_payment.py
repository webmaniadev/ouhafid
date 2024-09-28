# -*- coding: utf-8 -*-
# Powered by Kanak Infosystems LLP.
# © 2020 Kanak Infosystems LLP. (<https://www.kanakinfosystems.com>)

from odoo import models, fields, api, _
from odoo.exceptions import UserError


TYPES = [('check', 'Check'),
         ('effect', 'Effect'),
         ('transfer_payment', 'Transfer / Payment')]


class account_payment(models.Model):
    _inherit = "account.payment"

    operation_type = fields.Selection(TYPES, string="Operation Type")
    operation_number = fields.Char(string="Operation Number")
    operation_date = fields.Date(string="Operation Date")
    journal_type = fields.Selection(related='journal_id.type', string="Type")
    sale_id = fields.Many2one('sale.order', 'Sale Order', readonly=True)
    sale_count = fields.Integer(string='SaleOrder', compute='_get_saleorder_count', readonly=True)

    def _get_saleorder_count(self):
        for record in self:
            record.sale_count = 1

    def action_view_saleorder(self):
        action = self.env.ref('sale.action_quotations_with_onboarding').read([])[0]
        action['domain'] = [('id', '=', self.sale_id.id)]
        return action

    def unlink(self):
        if self._context.get('do_not_unlink_payment'):
            raise UserError(_('You cannot delete payments from this menu!'))
        return super().unlink()

