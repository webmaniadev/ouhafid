from odoo import models, fields, api, _
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # def valider_vente(self):
    #     super(SaleOrder, self).valider_vente()
    #     self.env.cr.execute("""
    #       UPDATE account_move
    #       SET name =
    #
    #
    #     """)



