from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import logging as log

class StockMove(models.Model):
    _inherit = 'stock.move'

    price_tax = fields.Float(compute='compute_price_tax', string='Total Tax', readonly=True, store=True)
    #price_tax_pret = fields.Float(compute='compute_price_tax_pret', string='Total Tax', readonly=True, store=True)

   
    @api.depends('quantity_done','product_uom_qty')
    def compute_price_tax(self):
        """
        Compute the amounts of the SO line.
        """


        for line in self:
            if line.quantity_done == 0:
                qte = line.product_uom_qty
            else:
                qte = line.quantity_done
            if line.sale_line_id:
                price = line.sale_line_id.price_unit * (1 - (line.sale_line_id.discount or 0.0) / 100.0)
                taxes = line.sale_line_id.tax_id.compute_all(price, 
                                                            line.sale_line_id.order_id.currency_id, 
                                                            qte, 
                                                            product=line.product_id, 
                                                            partner=line.sale_line_id.order_id.partner_shipping_id)
                line.update({
                    'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                    
                })
