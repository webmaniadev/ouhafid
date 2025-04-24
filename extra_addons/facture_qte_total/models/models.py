# -*- coding: utf-8 -*-

from odoo import models, fields, api



class AccountMove(models.Model):
    _inherit = 'account.move'

    total_quantity = fields.Float(
        string='Total Quantity',
        compute='_compute_total_quantity',
        store=False
    )
    @api.depends('invoice_line_ids.quantity')
    def _compute_total_quantity(self):
        for move in self:
            move.total_quantity = sum(move.invoice_line_ids.mapped('quantity'))


