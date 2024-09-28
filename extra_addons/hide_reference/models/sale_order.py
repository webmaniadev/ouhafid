
from odoo import api, models

class SaleOrderInherit(models.Model):
    _inherit = 'sale.order.line'

    @api.onchange('product_id')
    def product_id_change(self):
        res = super(SaleOrderInherit, self).product_id_change()
        if self.product_id.description_sale:
            self.name = self.product_id.description_sale
        else:
            self.name = self.product_id.name
        return res