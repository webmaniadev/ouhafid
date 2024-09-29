
from odoo import models, fields

class ResUsers(models.Model):
    _inherit = 'res.users'

    allow_sale_order_creation = fields.Boolean(string="Allow Sale Order Creation", default=True)
