# -*- coding: utf-8 -*-

from odoo import models, fields, api


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    total_quantity = fields.Float(
        string='Total Quantity',
        compute='_compute_total_quantity',
        store=False
    )


    total_quantity_package = fields.Float(
        string='Total Quantity',
        compute='_compute_total_quantity_package',
        store=False
    )

    @api.depends('move_ids_without_package.product_uom_qty')
    def _compute_total_quantity(self):
        for picking in self:
            picking.total_quantity = sum(picking.move_ids_without_package.mapped('product_uom_qty'))

    @api.depends('move_line_ids.qty_done', 'move_line_ids.product_uom_qty', 'state')
    def _compute_total_quantity_package(self):
         for picking in self:
            if picking.state == 'done':
                picking.total_quantity_package = sum(picking.move_line_ids.mapped('qty_done'))
            else:
                picking.total_quantity_package = sum(picking.move_line_ids.mapped('product_uom_qty'))


