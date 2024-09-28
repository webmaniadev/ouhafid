from odoo import models, fields, api, _
from odoo.exceptions import UserError

class AccountTax(models.Model):
    _inherit = 'account.tax'

    account_id = fields.Many2one('account.account', domain=[('deprecated', '=', False)], string='Tax Account', ondelete='restrict',
        help="Account that will be set on invoice tax lines for invoices. Leave empty to use the expense account.", oldname='account_collected_id')
    refund_account_id = fields.Many2one('account.account', domain=[('deprecated', '=', False)], string='Tax Account on Credit Notes', ondelete='restrict',
        help="Account that will be set on invoice tax lines for credit notes. Leave empty to use the expense account.", oldname='account_paid_id')
    tag_ids = fields.Many2many('account.account.tag', 'account_tax_account_tag', string='Tags', help="Optional tags you may want to assign for custom reporting")
    
    def get_grouping_key(self, invoice_tax_val):
        """ Returns a string that will be used to group account.invoice.tax sharing the same properties"""
        self.ensure_one()
        return str(invoice_tax_val['tax_id']) + '-' + \
               str(invoice_tax_val['account_id']) + '-' + \
               str(invoice_tax_val['account_analytic_id']) + '-' + \
               str(invoice_tax_val.get('analytic_tag_ids', []))