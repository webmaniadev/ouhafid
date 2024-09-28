from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AccountInvoice(models.Model):
    _inherit = 'account.move'

    def check_minimum_price(self):
        for line in self.invoice_line_ids:
            if line.product_id and (line.price_unit < line.product_id.minimum_price):
                raise UserError(
                    _("Le prix est inférieur au prix minimum du produit! \n Revérifiez s'il vous plait %s") % (line.product_id.name))
        return True

    def action_post(self):
        if self.move_type == 'out_invoice':
            self.check_minimum_price()
        # Call the original function without overriding
        return super(AccountInvoice, self).action_post()
