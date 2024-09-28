from odoo.exceptions import UserError
from odoo import models, fields, api, _
from itertools import groupby
from odoo.tools import float_is_zero, float_compare, pycompat

import logging as log

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    est_vente_detail = fields.Boolean(
        string='Paiements sur Bon de commande',
        default=False,
        copy=False,
    )

    etat_vente = fields.Selection(
        string='État de la vente',
        selection=[
            ('en_attente', 'En attente'),
            ('ouvert', 'Ouvert'),
            ('done', 'Terminer'),
        ],
        default='en_attente',
        copy=False,
    )

    payment_state_valued = fields.Selection(
        string="État de paiement",
        selection=[
            ('unpaid', 'Non payé'),
            ('partial_paid', 'Partiellement payé'),
            ('paid', 'Payé'),
        ],
        compute="compute_payment_state_valued")

    @api.depends('amount_total','residual_amount')
    def compute_payment_state_valued(self):
        for record in self:
            if record.est_vente_detail:
                if record.amount_total == record.residual_amount:
                    record.payment_state_valued = 'unpaid'
                if record.residual_amount == 0.0 and record.etat_vente == 'done':
                    record.payment_state_valued = 'paid'
                if record.residual_amount == 0.0 and record.etat_vente != 'done':
                    record.payment_state_valued = 'unpaid'
                if record.residual_amount > 0.0 and record.residual_amount < record.amount_total:
                    record.payment_state_valued = 'partial_paid'
            else:
                record.payment_state_valued = 'unpaid'



    @api.model
    def _default_journal(self):
        if self._context.get('default_journal_id', False):
            return self.env['account.journal'].browse(self._context.get('default_journal_id'))
        company_id = self._context.get('company_id', self.env.user.company_id.id)
        domain = [('type','=','sale'),('company_id', '=', company_id)]
        return self.env['account.journal'].search(domain, limit=1)

    journal_id = fields.Many2one(
        'account.journal',
        string='Journal',
        required=True,
        readonly=True,
        default=_default_journal
    )

    move_id = fields.Many2one(
        'account.move',
        string='Écriture du journal',
        readonly=True,
        index=True,
        ondelete='restrict',
        copy=False,
        help="Link to the automatically generated Journal Items."
    )

    move_name = fields.Char(
        string="Nom de l'écriture du journal",
        readonly=False,
        default=False,
        copy=False,
        help="Technical field holding the number given to the sale, automatically set when the sale is validated then stored to set the same number again if the sale is cancelled, set to draft and re-validated."
    )

    def action_register_payment(self): 

        action = {
                'name': _('Enregistrer un paiement'),
                'view_mode': 'form',
                'res_model': 'sale.order.payment',
                'view_id': self.env.ref('eloapps_sale_order_payment.wizard_sale_order_payment').id,
                'type': 'ir.actions.act_window',
                
                'context': {
                        'default_order_id': self.id,
                        'default_payment_amount': self.residual_amount,
                        'default_memo': self.move_id.name,
                    },
                'target': 'new'
            }
        return action


    def _get_aml_for_register_payment(self):
        self.ensure_one()
        return self.move_id.line_ids.filtered(lambda r: not r.reconciled and r.account_id.internal_type in ('payable', 'receivable'))


    def register_payment(self, payment_line, writeoff_acc_id=False, writeoff_journal_id=False):
        line_to_reconcile = self.env['account.move.line']

        for order in self:
            line_to_reconcile += order._get_aml_for_register_payment()

        return (line_to_reconcile + payment_line).reconcile(writeoff_acc_id, writeoff_journal_id)

    def _get_aml_for_amount_residual(self):
        for record in self:

            return record.sudo().move_id.line_ids.filtered(lambda l: l.account_id == record.partner_id.property_account_receivable_id)

 
    @api.depends(
        'state', 'currency_id', 'order_line.price_subtotal',
        'move_id.line_ids.amount_residual',
        'move_id.line_ids.currency_id')
    def _compute_residual(self):
        for record in self:
            residual_amount = 0.0
            for line in record._get_aml_for_amount_residual():
                if line.currency_id == record.currency_id:
                    residual_amount += line.amount_residual_currency if line.currency_id else line.amount_residual
                else:
                    from_currency = (line.currency_id and line.currency_id.with_context(date=line.create_date)) or line.company_id.currency_id.with_context(date=line.create_date)
                    residual_amount += from_currency.compute(line.amount_residual, record.currency_id)
                reconciled = False
                digits_rounding_precision = line.move_id.company_id.currency_id.rounding
                if float_is_zero(record.residual_amount, precision_rounding=digits_rounding_precision):
                    if line.currency_id and line.amount_currency:
                        if float_is_zero(line.amount_residual_currency, precision_rounding=line.currency_id.rounding):
                            reconciled = True
                        else:
                            reconciled = True
                record.reconciled = reconciled
            record.residual_amount = abs(residual_amount)
        
         
            digits_rounding_precision = record.currency_id.rounding
            
            if record.residual_amount > 0 :
                record.reconciled = False
            else :
                record.reconciled = True 
            # else:
            #     if float_is_zero(self.residual_amount, precision_rounding=digits_rounding_precision):
            #         self.reconciled = True
            #     else:
            #         self.reconciled = False



    residual_amount = fields.Monetary(
        string='Montant dù',
        compute='_compute_residual',
        store=True,
        help="Remaining amount due."
    )

    reconciled = fields.Boolean(
        string='Paid/Reconciled',
        store=True,
        readonly=True,
        compute='_compute_residual',
        help="It indicates that the invoice has been paid and the journal entry of the invoice has been reconciled with one or several journal entries of payment."
    )

    def _compute_payment_ids(self):
        for sale in self:
            payment_ids = self.env['account.payment'].search([('order_ids','=',sale.id)])
            
            payment_ids = payment_ids.mapped('line_ids').filtered(lambda aml_id: aml_id.account_id == sale.partner_id.property_account_receivable_id)
            self.payment_ids = [(6, 0, payment_ids.ids)]

    payment_ids = fields.Many2many(
        'account.move.line',
        string='Réglements',
        compute='_compute_payment_ids',
    )
    acc_payment_ids = fields.Many2many('account.payment')


    @api.constrains('move_id', 'reconciled')
    def onchange_reconciled(self):
        for record in self:
            if record.move_id and record.reconciled:
                record.write({'etat_vente': 'done'})

    def _get_invoiceable_lines(self, final=False):
        """Return the invoiceable lines for order `self`."""
        invoiceable_line_ids = []
        pending_section = None
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')

        for line in self.order_line:
            if line.display_type == 'line_section':
                # Only invoice the section if one of its lines is invoiceable
                pending_section = line
                continue
            if line.display_type != 'line_note' and float_is_zero(line.qty_to_invoice, precision_digits=precision):
                continue
            if line.qty_to_invoice > 0 or (line.qty_to_invoice < 0 and final) or line.display_type == 'line_note':
                if pending_section:
                    invoiceable_line_ids.append(pending_section.id)
                    pending_section = None
                invoiceable_line_ids.append(line.id)
        
        return self.env['sale.order.line'].browse(invoiceable_line_ids)

    def _create_invoices(self, grouped=False, final=False):
        """
        Create the invoice associated to the SO.
        :param grouped: if True, invoices are grouped by SO id. If False, invoices are grouped by
                        (partner_invoice_id, currency)
        :param final: if True, refunds will be generated if necessary
        :returns: list of created invoices
        """
        if not self.env['account.move'].check_access_rights('create', False):
            try:
                self.check_access_rights('write')
                self.check_access_rule('write')
            except AccessError:
                return self.env['account.move']

        # 1) Create invoices.
        invoice_vals_list = []
        for order in self:
            if order.est_vente_detail == True:
                journal = self.env['account.journal'].search([('pour_vente_detail','=',True)], limit=1)
            else:
                journal = self.env['account.journal'].search([('pour_vente_detail','=',False)], limit=1)

            invoice_vals = order._prepare_invoice()
            invoiceable_lines = order._get_invoiceable_lines(final)

            if not invoiceable_lines and not invoice_vals['invoice_line_ids']:
                raise UserError(_('There is no invoiceable line. If a product has a Delivered quantities invoicing policy, please make sure that a quantity has been delivered.'))

            # there is a chance the invoice_vals['invoice_line_ids'] already contains data when
            # another module extends the method `_prepare_invoice()`. Therefore, instead of
            # replacing the invoice_vals['invoice_line_ids'], we append invoiceable lines into it
            invoice_vals['invoice_line_ids'] += [
                (0, 0, line._prepare_invoice_line())
                for line in invoiceable_lines
            ]
            invoice_vals['journal_id'] =  journal.id
            invoice_vals_list.append(invoice_vals)


        if not invoice_vals_list:
            raise UserError(_(
                'There is no invoiceable line. If a product has a Delivered quantities invoicing policy, please make sure that a quantity has been delivered.'))

        # 2) Manage 'grouped' parameter: group by (partner_id, currency_id).
        if not grouped:
            new_invoice_vals_list = []
            invoice_grouping_keys = self._get_invoice_grouping_keys()
            invoice_vals_list = sorted(invoice_vals_list, key=lambda x: [x.get(grouping_key) for grouping_key in invoice_grouping_keys])
            for grouping_keys, invoices in groupby(invoice_vals_list, key=lambda x: [x.get(grouping_key) for grouping_key in invoice_grouping_keys]):
                origins = set()
                payment_refs = set()
                refs = set()
                ref_invoice_vals = None
                for invoice_vals in invoices:
                    if not ref_invoice_vals:
                        ref_invoice_vals = invoice_vals
                    else:
                        ref_invoice_vals['invoice_line_ids'] += invoice_vals['invoice_line_ids']
                    origins.add(invoice_vals['invoice_origin'])
                    payment_refs.add(invoice_vals['payment_reference'])
                    refs.add(invoice_vals['ref'])
                ref_invoice_vals.update({
                    'ref': ', '.join(refs)[:2000],
                    'invoice_origin': ', '.join(origins),
                    'payment_reference': len(payment_refs) == 1 and payment_refs.pop() or False,
                })
                new_invoice_vals_list.append(ref_invoice_vals)
            invoice_vals_list = new_invoice_vals_list

        # 3) Create invoices.

        # As part of the invoice creation, we make sure the sequence of multiple SO do not interfere
        # in a single invoice. Example:
        # SO 1:
        # - Section A (sequence: 10)
        # - Product A (sequence: 11)
        # SO 2:
        # - Section B (sequence: 10)
        # - Product B (sequence: 11)
        #
        # If SO 1 & 2 are grouped in the same invoice, the result will be:
        # - Section A (sequence: 10)
        # - Section B (sequence: 10)
        # - Product A (sequence: 11)
        # - Product B (sequence: 11)
        #
        # Resequencing should be safe, however we resequence only if there are less invoices than
        # orders, meaning a grouping might have been done. This could also mean that only a part
        # of the selected SO are invoiceable, but resequencing in this case shouldn't be an issue.

        # if self.est_vente_detail == True:
        #     journal = self.env['account.journal'].search([('pour_vente_detail','=',True)], limit=1)
        # else:
        #     journal = self.env['account.journal'].search([('pour_vente_detail','=',False)], limit=1)


        if len(invoice_vals_list) < len(self):
            SaleOrderLine = self.env['sale.order.line']
            for invoice in invoice_vals_list:
                sequence = 1
                for line in invoice['invoice_line_ids']:
                    line[2]['sequence'] = SaleOrderLine._get_invoice_line_sequence(new=sequence, old=line[2]['sequence'])
                    sequence += 1

        # Manage the creation of invoices in sudo because a salesperson must be able to generate an invoice from a
        # sale order without "billing" access rights. However, he should not be able to create an invoice from scratch.

        # invoice_vals_list[0].update(
        #     {
        #     # 'name': name,
        #     'journal_id': journal.id,

        #     })

        moves = self.env['account.move'].sudo().with_context(default_type='out_invoice').create(invoice_vals_list)

        # 4) Some moves might actually be refunds: convert them if the total amount is negative
        # We do this after the moves have been created since we need taxes, etc. to know if the total
        # is actually negative or not
        if final:
            moves.sudo().filtered(lambda m: m.amount_total < 0).action_switch_invoice_into_refund_credit_note()
        for move in moves:
            move.message_post_with_view('mail.message_origin_link',
                values={'self': move, 'origin': move.line_ids.mapped('sale_line_ids.order_id')},
                subtype_id=self.env.ref('mail.mt_note').id
            )
        return moves


    def valider_vente(self):
        journal_id = self.env['account.journal'].search([('pour_vente_detail','=',True)], limit=1)
        if not journal_id:
            raise UserError('Veuillez choisir un journal a utiliser pour la vente au détail.')
        self.update({'journal_id': journal_id.id})

        a =self._create_invoices()
        for line in self.order_line:

            line.qty_invoiced = line.product_uom_qty
        self.update({
            'etat_vente' : 'ouvert',
            'invoice_status': 'no',
            'move_id': a.id, 
            })


    def cree_facture_vente(self):
        for order in self:
            order.move_id.move_type = 'out_invoice'
            order.est_vente_detail = False
            journal = self.env['account.journal'].search([('type', '=','sale' )], limit = 1)
            to_write = {'state': 'posted'}
            to_write['journal_id'] = journal.id

            order.move_id.write(to_write)
            if order.move_id.name :
                # Get the journal's sequence.
                order.move_id._compute_name()
        return 


    @api.model
    def sale_line_move_line_get(self):
        res = []
        for line in self.order_line:
            if line.product_uom_qty==0:
                continue
            tax_ids = []
            for tax in line.tax_id:
                tax_ids.append((4, tax.id, None))
                for child in tax.children_tax_ids:
                    if child.type_tax_use != 'none':
                        tax_ids.append((4, child.id, None))
            analytic_tag_ids = [(4, analytic_tag.id, None) for analytic_tag in line.analytic_tag_ids]
           
            move_line_dict = {
                'orderl_id': line.id,
                'type': 'src',
                'name': line.name.split('\n')[0][:64],
                'price_unit': line.price_unit,
                'product_uom_qty': line.product_uom_qty,
                'price': line.price_subtotal,
                'account_id': line.order_id.journal_id.default_debit_account_id.id,
                'product_id': line.product_id.id,
                'uom_id': line.product_id.uom_id.id,
                'account_analytic_id': line.order_id.analytic_account_id.id,
                'tax_ids': tax_ids,
                'order_id': self.id,
                'analytic_tag_ids': analytic_tag_ids
            }
            res.append(move_line_dict)
        return res

    def _prepare_tax_line_vals(self, line, tax):
        vals = {
            
            'name': tax['name'],
            'tax_id': tax['id'],
            'amount': tax['amount'],
            'base': tax['base'],
            'manual': False,
            'sequence': tax['sequence'],
            'account_analytic_id': tax['analytic'] and line.order_id.analytic_account_id.id or False,
            'account_id': tax['account_id'],
        }
        return vals


    def get_taxes_values(self):
        tax_grouped = {}
        round_curr = self.currency_id.round
        for line in self.order_line:
            price_unit = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            taxes = line.tax_id.compute_all(price_unit, self.currency_id, line.product_uom_qty, line.product_id, self.partner_id)['taxes']
            for tax in taxes:
                val = self._prepare_tax_line_vals(line, tax)
               
                key = self.env['account.tax'].browse(tax['id']).get_grouping_key(val)

                if key not in tax_grouped:
                    tax_grouped[key] = val
                    tax_grouped[key]['base'] = round_curr(val['base'])
                else:
                    tax_grouped[key]['amount'] += val['amount']
                    tax_grouped[key]['base'] += round_curr(val['base'])
        return tax_grouped

    @api.model
    def tax_line_move_line_get(self):
        res = []
        done_taxes = []

        taxes_grouped = self.get_taxes_values()
        tax_lines = self.env['account.invoice.tax']
        for tax in taxes_grouped.values():
            tax_lines += tax_lines.new(tax)

        for tax_line in tax_lines:
            if tax_line.amount_total:
                tax = tax_line.tax_id
                if tax.amount_type == "group":
                    for child_tax in tax.children_tax_ids:
                        done_taxes.append(child_tax.id)
                res.append({
                    'invoice_tax_line_id': tax_line.id,
                    'tax_line_id': tax_line.tax_id.id,
                    'type': 'tax',
                    'name': tax_line.name,
                    'price_unit': tax_line.amount_total,
                    'quantity': 1,
                    'price': tax_line.amount_total,
                    'account_id': tax_line.account_id.id,
                    'account_analytic_id': tax_line.account_analytic_id.id,
                    'order_id': self.id,
                    'tax_ids': [(6, 0, list(done_taxes))] if tax_line.tax_id.include_base_amount else []
                })
                done_taxes.append(tax.id)

        return res


    def compute_sale_totals(self, company_currency, sale_move_lines):
        total = 0
        total_currency = 0
        for line in sale_move_lines:
            if self.currency_id != company_currency:
                currency = self.currency_id.with_context(date=self._get_currency_rate_date() or fields.Date.context_today(self))
                if not (line.get('currency_id') and line.get('amount_currency')):
                    line['currency_id'] = currency.id
                    line['amount_currency'] = currency.round(line['price'])
                    line['price'] = currency.compute(line['price'], company_currency)
            else:
                line['currency_id'] = False
                line['amount_currency'] = False
                line['price'] = self.currency_id.round(line['price'])

            total += line['price']
            total_currency += line['amount_currency'] or line['price']
            line['price'] = - line['price']

        return total, total_currency, sale_move_lines

    @api.model
    def line_get_convert(self, line, part):
        return self.env['product.product']._convert_prepared_anglosaxon_line(line, part)

    def action_move_create(self):
        account_move = self.env['account.move']

        for sale in self:
            if not sale.journal_id.sequence_id:
                raise UserError(_('Please define sequence on the journal related to this invoice.'))
            if not sale.order_line:
                raise UserError(_('Please create some sale lines.'))
            if sale.move_id:
                continue

            ctx = dict(self._context, lang=sale.partner_id.lang)
            company_currency = sale.company_id.currency_id

            sml = sale.sale_line_move_line_get()
            sml = sml + sale.tax_line_move_line_get()

            diff_currency = sale.currency_id != company_currency

            total, total_currency, sml = sale.with_context(ctx).compute_sale_totals(company_currency, sml)

            name = sale.name or '/'
            if sale.payment_term_id:
                totlines = sale.with_context(ctx).payment_term_id.with_context(currency_id=company_currency.id).compute(total, sale.date_order)[0]
                res_amount_currency = total_currency
                ctx['date'] = sale.date_order

                for i, t in enumerate(totlines):
                    if sale.currency_id != company_currency:
                        amount_currency = company_currency.with_context(ctx).compute(totlines[1], sale.currency_id)
                    else:
                        amount_currency = False

                    res_amount_currency -= amount_currency or 0
                    if i + 1 == len(totlines):
                        amount_currency += res_amount_currency
                    
                    sml.append({
                        'type': 'dest',
                        'name': name,
                        'price': totlines[1],
                        'account_id': sale.partner_id.property_account_receivable_id.id,
                        'date_maturity': totlines[0],
                        'amount_currency': diff_currency and amount_currency,
                        'currency_id': diff_currency and sale.currency_id.id,
                        'order_id': sale.id
                    })
                    break
            else:
                sml.append({
                    'type': 'dest',
                    'name': name,
                    'price': total,
                    'account_id': sale.partner_id.property_account_receivable_id.id,
                    'date_maturity': sale.date_order,
                    'amount_currency': diff_currency and total_currency,
                    'currency_id': diff_currency and sale.currency_id.id,
                    'order_id': sale.id
                })

            part = self.env['res.partner']._find_accounting_partner(sale.partner_id)
            line = [(0, 0, self.line_get_convert(l, part.id)) for l in sml]


            journal = sale.journal_id.with_context(ctx)

            date = sale.date_order
            move_vals = {
                'ref': sale.client_order_ref,
                'line_ids': line,
                'journal_id': journal.id,
                'date': date,
                'narration': sale.note,
                'name': sale.name,
            }
            ctx['company_id'] = sale.company_id.id
            ctx['sale'] = sale
            ctx_nolang = ctx.copy()
            ctx_nolang.pop('lang', None)
         
            move = account_move.with_context(ctx_nolang).create(move_vals)
            move.post()

            vals = {
                'move_id': move.id,
                'move_name': move.name,
            }
            sale.with_context(ctx).write(vals)
        return True

    def print_report_cmd(self):
        return self.env.ref('eloapps_sale_order_payment.sale_valued').report_action(self)
