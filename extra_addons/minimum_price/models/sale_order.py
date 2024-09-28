from odoo import api, fields, models, _
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def check_min_price(self):
        for order in self:
            for line in order.order_line:
                if line.product_id and (line.price_unit < line.product_id.minimum_price):
                    raise UserError(_("Le prix est inférieur au prix minimum du produit! Revérifiez s'il vous plait %s") % (line.product_id.name))

        return True

    def action_confirm(self):
        self.check_min_price()
        return super(SaleOrder, self).action_confirm()
