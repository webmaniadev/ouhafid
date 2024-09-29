
from odoo import models, fields

class ResUsers(models.Model):
    _inherit = 'res.users'

    allow_sale_order_creation = fields.Boolean(string="Allow Sale Order Creation", default=True)

    def action_check_sale_order_creation(self):
        # Vérifiez si l'utilisateur est dans un groupe autorisé
        return self.env.user.has_group('base.group_sale_manager')
