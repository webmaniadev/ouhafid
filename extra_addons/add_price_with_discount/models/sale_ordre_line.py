from odoo import models, fields, api

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    prix_unitaire_with_discount = fields.Float(
        string='Prix Unitaire avec remise',
        compute='_compute_prix_unitaire_with_discount'
    )
    @api.depends('price_subtotal', 'product_uom_qty')
    def _compute_prix_unitaire_with_discount(self):
        for line in self:
            if line.product_uom_qty:
                line.prix_unitaire_with_discount = line.price_total  / line.product_uom_qty
            else:
                line.prix_unitaire_with_discount = 0.0
