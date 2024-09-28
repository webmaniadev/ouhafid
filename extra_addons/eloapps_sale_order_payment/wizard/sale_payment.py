import time

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class SaleAdvancePaymentInvExt(models.TransientModel):
    _inherit = "sale.advance.payment.inv"


    def create_invoices(self):
        sale_orders = self.env['sale.order'].browse(self._context.get('active_ids', []))
        for order in sale_orders:
            if order.est_vente_detail:
                raise UserError(_('Cette action ne gère pas les devis en détail.'))
        super(SaleAdvancePaymentInvExt, self).create_invoices()
        

                # order.etat_vente = 'ouvert'
                # order.move_id = order.invoice_ids.id
                # order.move_id.move_type = 'entry'
                

                # journal_id = self.env['account.journal'].search([('pour_vente_detail','=',True)], limit=1)
                # if not journal_id:
                #     raise UserError('Please choose a journal to use for sale order payment.')

                # order.move_id.journal_id = journal_id.id

                # order.move_id.action_post()
        


        return {'type': 'ir.actions.act_window_close'}

