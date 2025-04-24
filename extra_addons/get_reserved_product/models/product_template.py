# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    ready_picking_count = fields.Integer(string='Reserved Deliveries', compute='_compute_ready_picking_count')

    def _compute_ready_picking_count(self):
        for product in self:
            # Find stock moves for this specific product that are in 'assigned' state
            domain = [
                ('state', '=', 'assigned'),  # assigned = Ready/Reserved state
                ('product_id', 'in', product.product_variant_ids.ids)
            ]
            # Count stock moves matching our criteria
            moves = self.env['stock.move'].search(domain)
            # Get unique picking_ids (delivery orders) containing these moves
            picking_ids = moves.mapped('picking_id').filtered(lambda p: p.state == 'assigned')
            product.ready_picking_count = len(picking_ids)

    def action_view_ready_deliveries(self):
        self.ensure_one()
        # First get the relevant stock moves
        domain = [
            ('state', '=', 'assigned'),
            ('product_id', 'in', self.product_variant_ids.ids)
        ]
        moves = self.env['stock.move'].search(domain)
        # Then get the unique picking_ids
        picking_ids = moves.mapped('picking_id').filtered(lambda p: p.state == 'assigned')

        action = {
            'name': _('Reserved Deliveries'),
            'type': 'ir.actions.act_window',
            'res_model': 'stock.picking',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', picking_ids.ids)],
        }
        return action

class ProductProduct(models.Model):
    _inherit = 'product.product'

    def action_view_ready_deliveries(self):
        # Implementation here
        self.ensure_one()
        action = self.env.ref('stock.action_picking_tree_ready').read()[0]
        action['domain'] = [('product_id', '=', self.id), ('state', '=', 'assigned')]
        return action