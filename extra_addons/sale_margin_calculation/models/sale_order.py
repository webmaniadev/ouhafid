from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    exclude_product = fields.Boolean(compute='_compute_exclude_product', store=True)

    @api.depends('product_id', 'price_subtotal', 'product_uom_qty', 'purchase_price', 'discount',
                 'product_id.product_tmpl_id',
                 'order_id.pricelist_id')
    def _compute_margin(self):
        for line in self:
            exclude_product = False
            pricelist_items = self.env['product.pricelist.item'].search(
                [('pricelist_id', '=', line.order_id.pricelist_id.id),
                 ('product_tmpl_id', '=', line.product_id.product_tmpl_id.id),
                 ('date_start', '<=', line.order_id.date_order),
                 '|', ('date_end', '>=', line.order_id.date_order), ('date_end', '=', False)
                 ])
            if pricelist_items:
                exclude_product = any(item.exclude_product_test for item in pricelist_items)

            if exclude_product:
                subtotal_without_discount = line.price_unit / (1 + 0.2) * line.product_uom_qty
                margin = subtotal_without_discount - (line.purchase_price * line.product_uom_qty)
                if subtotal_without_discount == 0:
                    margin_percent = 0
                else:
                    margin_percent = margin / subtotal_without_discount
                line.margin = margin
                line.margin_percent = margin_percent
            else:
                line.margin = line.price_subtotal - (line.purchase_price * line.product_uom_qty)
                line.margin_percent = line.price_subtotal and line.margin / line.price_subtotal


    @api.depends('product_id', 'order_id.pricelist_id', 'order_id.date_order')
    def _compute_exclude_product(self):
        for line in self:
            exclude_product = True
            pricelist_items = self.env['product.pricelist.item'].search(
                [('pricelist_id', '=', line.order_id.pricelist_id.id),
                 ('product_tmpl_id', '=', line.product_id.product_tmpl_id.id),
                 ('date_start', '<=', line.order_id.date_order),
                 '|', ('date_end', '>=', line.order_id.date_order), ('date_end', '=', False)
                 ])
            if pricelist_items :
                if line.product_id:
                    exclude_product = any(item.exclude_product_test for item in pricelist_items)
                else:
                    exclude_product = False
            line.exclude_product = exclude_product
class SaleOrder(models.Model):
    _inherit = "sale.order"
    margin_percent = fields.Float(
        "Margin (%)", compute='_compute_margin', store=True, group_operator='avg')

    # margin = fields.Float(compute='_compute_margin', store=True)
    # pricelist_items = fields.Boolean(compute='_compute_margin', store=True)

    @api.depends('order_line.margin', 'amount_untaxed', 'order_line.product_id.product_tmpl_id', 'pricelist_id')
    def _compute_margin(self):
        for order in self:
            order.margin = sum(order.order_line.mapped('margin'))
            amount_untaxed_without_discount = 0
            for line in order.order_line:
                exclude_product = False
                pricelist_items = self.env['product.pricelist.item'].search(
                    [('pricelist_id', '=', order.pricelist_id.id),
                     ('product_tmpl_id', '=', line.product_id.product_tmpl_id.id),
                     ('date_start', '<=', line.order_id.date_order),
                     '|', ('date_end', '>=', line.order_id.date_order), ('date_end', '=', False)
                     ])
                if pricelist_items:
                    exclude_product = any(item.exclude_product_test for item in pricelist_items)
                if exclude_product:
                    # Calculating the price without discount
                    amount_untaxed_without_discount += line.price_unit / (1 + 0.2) * line.product_uom_qty
                else:
                    amount_untaxed_without_discount += line.price_subtotal
            order.margin_percent = amount_untaxed_without_discount and (
                        order.margin / amount_untaxed_without_discount) or 0
