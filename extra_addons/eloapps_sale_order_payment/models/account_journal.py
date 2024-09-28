from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class AccountJournal(models.Model):
    _inherit = 'account.journal'

    pour_vente_detail = fields.Boolean(
        string='Use for sale order payments',
    )
    post_at = fields.Selection([('pay_val', 'Payment Validation'), ('bank_rec', 'Bank Reconciliation')], string="Post At", default='pay_val')

    @api.constrains('pour_vente_detail')
    def constrains_pour_vente_detail(self):
        if self.pour_vente_detail and self.env['account.journal'].search([('pour_vente_detail','=',True), ('id','!=',self.id)]):
            raise ValidationError('Utiliser pour les paiements sur bon de commande ne doit être coché que sur un seul journal.')


