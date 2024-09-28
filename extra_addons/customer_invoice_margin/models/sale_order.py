from odoo import models, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _prepare_invoice(self):
        invoice_vals = super(SaleOrder, self)._prepare_invoice()
        invoice_vals['pricelist_id'] = self.pricelist_id.id
        return invoice_vals