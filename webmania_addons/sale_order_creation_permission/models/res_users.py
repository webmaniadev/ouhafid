
from odoo import models, fields, api, exceptions

class ResUsers(models.Model):
    _inherit = 'res.users'

    allow_sale_order_creation = fields.Boolean(string="Allow Sale Order Creation", default=True)

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def create(self, vals):
        if not self.env.user.allow_sale_order_creation:
            raise exceptions.UserError("You don't have permission to create sale orders.")
        return super(SaleOrder, self).create(vals)
