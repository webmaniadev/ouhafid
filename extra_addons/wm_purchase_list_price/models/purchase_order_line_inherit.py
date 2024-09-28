# -*- coding: utf-8 -*-
from odoo import fields, models,api


class InheritProductTemplate(models.Model):
    _inherit = "product.template"
    new_price = fields.Boolean(string="Nouveau Prix De Vente", default=False)
    last_price = fields.Float(string="Ancien Prix De Vente", readonly=True)
    
class InheritPurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"
    list_price = fields.Float(
        "Prix De Vente ", readonly=False
    )
    @api.onchange('product_id')
    def product_related_fields(self):

        if self.product_id:

            self.list_price = self.product_id.list_price

class InheritPurchaseOrderLine(models.Model):
    _inherit = "purchase.order"

    def button_confirm(self):
        for el in self.order_line:
            product_data = {}
            product_id = el.product_id.id
            product_data["standard_price"] = el.price_unit
            product_data["list_price"] = el.list_price
            current_product = \
                self.env['product.product'].search([('id', '=', product_id)])
            old_list_price = current_product.list_price
            if old_list_price != el.list_price:
                product_data["new_price"] = True
                product_data["last_price"] = old_list_price
            updated_successfuly = current_product.write(product_data)
            return super(InheritPurchaseOrderLine, self).button_confirm()
