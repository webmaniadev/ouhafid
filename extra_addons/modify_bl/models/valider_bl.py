# -*- coding: utf-8 -*-

from odoo import models, fields, api, tools


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def button_validate(self):
        res = super(StockPicking, self).button_validate()

        for picking in self:
            if picking.state == 'done' and picking.sale_id and self.env['ir.config_parameter'].sudo().get_param('test_valider_delivery'):
                picking.sale_id.valider_vente()
                delivery_order_name = picking.name
            if picking.sale_id.move_id:
                account_moves = self.env['account.move'].search([('invoice_origin', '=', picking.sale_id.name)])
                if account_moves:
                   account_moves.write({'name': delivery_order_name})

        return res

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    test_valider_delivery = fields.Boolean(
        string="Valider la vente Basé sur Bon de livrasion",
        default=True,)

    @api.model
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        test_valider_delivery = self.test_valider_delivery

        # Set the global variable
        self.env['ir.config_parameter'].sudo().set_param('test_valider_delivery', test_valider_delivery)

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        test_valider_delivery = self.env['ir.config_parameter'].sudo().get_param('test_valider_delivery')
        res.update(
            test_valider_delivery=test_valider_delivery
        )
        return res


