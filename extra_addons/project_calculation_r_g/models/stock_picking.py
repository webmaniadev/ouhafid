from odoo import models, fields, api, _
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    apply_rg_on_amount_total = fields.Boolean(
        string='Appliquer RG sur montant total',
        default=False,
        help="Si cochée, la garantie de rétention sera appliquée au montant total"
    )

