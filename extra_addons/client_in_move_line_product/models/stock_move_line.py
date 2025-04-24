from odoo import models, fields, api


class StockMoveLineInherit(models.Model):
    _inherit = 'stock.move.line'

    partner_id = fields.Many2one(
        'res.partner',
        string='Client',
        related='picking_id.partner_id',
        store=True,
        readonly=True
    )
