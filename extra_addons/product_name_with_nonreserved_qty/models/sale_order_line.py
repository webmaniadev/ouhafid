# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ProductProduct(models.Model):
    _inherit = 'product.product'

    # Override name_search to include non-reserved quantity
    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        # First get original search results
        result = super(ProductProduct, self).name_search(
            name=name, args=args, operator=operator, limit=limit)

        # Use the fixed label
        sale_label = "VENTE"

        # Then modify the display names to include quantity with new format
        updated_result = []
        for product_id, product_name in result:
            product = self.browse(product_id)
            qty_not_reserved = product.qty_available_not_res
            qty_int = int(qty_not_reserved)

            # Format with the new format using colon
            name_with_qty = f"{product_name} - {sale_label}: {qty_int}"
            updated_result.append((product_id, name_with_qty))

        return updated_result