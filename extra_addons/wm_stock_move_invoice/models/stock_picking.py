# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2020-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: Sayooj A O(<https://www.cybrosys.com>)
#
#    You can modify it under the terms of the GNU AFFERO
#    GENERAL PUBLIC LICENSE (AGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU AFFERO GENERAL PUBLIC LICENSE (AGPL v3) for more details.
#
#    You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
#    (AGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################
from odoo import fields, models, _
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = 'stock.picking'
    invoice_count = fields.Integer(string='Invoices', compute='_compute_invoice_count')
    operation_code = fields.Selection(related='picking_type_id.code')
    has_invoiceable_qty = fields.Boolean(string='Has Invoiceable Quantity', compute='_compute_has_invoiceable_qty')

    is_return = fields.Boolean()


    def _compute_has_invoiceable_qty(self):
        """Check if there are any quantities left to invoice"""
        for picking in self:
            invoiceable_lines = picking._get_invoiceable_lines()
            picking.has_invoiceable_qty = bool(invoiceable_lines)

    def _compute_invoice_count(self):
        """This compute function used to count the number of invoice for the picking"""
        for picking_id in self:
            move_ids = picking_id.env['account.move'].search([('invoice_origin', '=', picking_id.name)])
            if move_ids:
                self.invoice_count = len(move_ids)
            else:
                self.invoice_count = 0

    def _get_invoiceable_lines(self):
        """Get lines that can still be invoiced"""
        self.ensure_one()
        invoiced_lines = self.env['account.move.line'].search([
            ('move_id.invoice_origin', '=', self.name),
            ('product_id', '!=', False)
        ])

        invoiceable_lines = []
        for move in self.move_ids_without_package:
            # Calculate already invoiced quantity for this product
            invoiced_qty = sum(
                invoiced_lines.filtered(
                    lambda l: l.product_id == move.product_id
                ).mapped('quantity')
            )
            # Calculate remaining quantity to invoice
            remaining_qty = move.quantity_done - invoiced_qty
            if remaining_qty > 0:
                invoiceable_lines.append({
                    'move': move,
                    'remaining_qty': remaining_qty
                })
        return invoiceable_lines

    def create_invoice(self):
        """Modified function to handle partial invoicing"""
        for picking_id in self:
            if picking_id.picking_type_id.code == 'outgoing':
                customer_journal_id = picking_id.env['ir.config_parameter'].sudo().get_param(
                    'wm_stock_move_invoice.customer_journal_id') or False
                if not customer_journal_id:
                    raise UserError(_("Please configure the journal from settings"))

                # Get invoiceable lines
                invoiceable_lines = picking_id._get_invoiceable_lines()
                if not invoiceable_lines:
                    raise UserError(_("Nothing left to invoice for this delivery order."))

                invoice_line_list = []
                for line in invoiceable_lines:
                    move = line['move']
                    remaining_qty = line['remaining_qty']

                    vals = (0, 0, {
                        'name': move.description_picking,
                        'product_id': move.product_id.id,
                        'price_unit': move.product_id.lst_price,
                        'account_id': move.product_id.property_account_income_id.id if move.product_id.property_account_income_id
                        else move.product_id.categ_id.property_account_income_categ_id.id,
                        'tax_ids': [(6, 0, [picking_id.company_id.account_sale_tax_id.id])],
                        'quantity': remaining_qty,
                    })
                    invoice_line_list.append(vals)

                invoice = picking_id.env['account.move'].create({
                    'move_type': 'out_invoice',
                    'invoice_origin': picking_id.name,
                    'invoice_user_id': self.env.uid,
                    'narration': picking_id.name,
                    'partner_id': picking_id.partner_id.id,
                    'currency_id': picking_id.env.user.company_id.currency_id.id,
                    'journal_id': int(customer_journal_id),
                    'payment_reference': picking_id.name,
                    'picking_id': picking_id.id,
                    'invoice_line_ids': invoice_line_list
                })
                return invoice

    def create_bill(self):
        """Modified function for creating vendor bill with partial quantities"""
        for picking_id in self:
            if picking_id.picking_type_id.code == 'incoming':
                vendor_journal_id = picking_id.env['ir.config_parameter'].sudo().get_param(
                    'wm_stock_move_invoice.vendor_journal_id') or False
                if not vendor_journal_id:
                    raise UserError(_("Please configure the journal from the settings."))

                # Get billable lines
                billable_lines = picking_id._get_billable_lines()
                if not billable_lines:
                    raise UserError(_("Nothing left to bill for this receipt."))

                invoice_line_list = []
                for line in billable_lines:
                    move = line['move']
                    remaining_qty = line['remaining_qty']

                    vals = (0, 0, {
                        'name': move.description_picking,
                        'product_id': move.product_id.id,
                        'price_unit': move.product_id.lst_price,
                        'account_id': move.product_id.property_account_expense_id.id if move.product_id.property_account_expense_id
                        else move.product_id.categ_id.property_account_expense_categ_id.id,
                        'tax_ids': [(6, 0, [picking_id.company_id.account_purchase_tax_id.id])],
                        'quantity': remaining_qty,
                    })
                    invoice_line_list.append(vals)

                invoice = picking_id.env['account.move'].create({
                    'move_type': 'in_invoice',
                    'invoice_origin': picking_id.name,
                    'invoice_user_id': self.env.uid,
                    'narration': picking_id.name,
                    'partner_id': picking_id.partner_id.id,
                    'currency_id': picking_id.env.user.company_id.currency_id.id,
                    'journal_id': int(vendor_journal_id),
                    'payment_reference': picking_id.name,
                    'picking_id': picking_id.id,
                    'invoice_line_ids': invoice_line_list
                })
                return invoice

    has_billable_qty = fields.Boolean(string='Has Billable Quantity', compute='_compute_has_billable_qty')

    def _compute_has_billable_qty(self):
        """Check if there are any quantities left to bill"""
        for picking in self:
            if picking.picking_type_id.code == 'incoming':
                billable_lines = picking._get_billable_lines()
                picking.has_billable_qty = bool(billable_lines)
            else:
                picking.has_billable_qty = False

    def create_customer_credit(self):
        """This is the function for creating customer credit note
                from the picking"""
        for picking_id in self:
            current_user = picking_id.env.uid
            if picking_id.picking_type_id.code == 'incoming':
                customer_journal_id = picking_id.env['ir.config_parameter'].sudo().get_param(
                    'wm_stock_move_invoice.customer_journal_id') or False
                if not customer_journal_id:
                    raise UserError(_("Please configure the journal from settings"))
                invoice_line_list = []
                for move_ids_without_package in picking_id.move_ids_without_package:
                    vals = (0, 0, {
                        'name': move_ids_without_package.description_picking,
                        'product_id': move_ids_without_package.product_id.id,
                        'price_unit': move_ids_without_package.product_id.lst_price,
                        'account_id': move_ids_without_package.product_id.property_account_income_id.id if move_ids_without_package.product_id.property_account_income_id
                        else move_ids_without_package.product_id.categ_id.property_account_income_categ_id.id,
                        'tax_ids': [(6, 0, [picking_id.company_id.account_sale_tax_id.id])],
                        'quantity': move_ids_without_package.quantity_done,
                    })
                    invoice_line_list.append(vals)
                invoice = picking_id.env['account.move'].create({
                    'move_type': 'out_refund',
                    'invoice_origin': picking_id.name,
                    'invoice_user_id': current_user,
                    'narration': picking_id.name,
                    'partner_id': picking_id.partner_id.id,
                    'currency_id': picking_id.env.user.company_id.currency_id.id,
                    'journal_id': int(customer_journal_id),
                    'payment_reference': picking_id.name,
                    'picking_id': picking_id.id,
                    'invoice_line_ids': invoice_line_list
                })
                return invoice

    def _get_billable_lines(self):
        """Get lines that can still be billed for vendor"""
        self.ensure_one()
        billed_lines = self.env['account.move.line'].search([
            ('move_id.invoice_origin', '=', self.name),
            ('move_id.move_type', '=', 'in_invoice'),
            ('product_id', '!=', False)
        ])

        billable_lines = []
        for move in self.move_ids_without_package:
            # Calculate already billed quantity for this product
            billed_qty = sum(
                billed_lines.filtered(
                    lambda l: l.product_id == move.product_id
                ).mapped('quantity')
            )
            # Calculate remaining quantity to bill
            remaining_qty = move.quantity_done - billed_qty
            if remaining_qty > 0:
                billable_lines.append({
                    'move': move,
                    'remaining_qty': remaining_qty
                })
        return billable_lines

    def create_vendor_credit(self):
        """This is the function for creating refund
                from the picking"""
        for picking_id in self:
            current_user = self.env.uid
            if picking_id.picking_type_id.code == 'outgoing':
                vendor_journal_id = picking_id.env['ir.config_parameter'].sudo().get_param(
                    'wm_stock_move_invoice.vendor_journal_id') or False
                if not vendor_journal_id:
                    raise UserError(_("Please configure the journal from the settings."))
                invoice_line_list = []
                for move_ids_without_package in picking_id.move_ids_without_package:
                    vals = (0, 0, {
                        'name': move_ids_without_package.description_picking,
                        'product_id': move_ids_without_package.product_id.id,
                        'price_unit': move_ids_without_package.product_id.lst_price,
                        'account_id': move_ids_without_package.product_id.property_account_income_id.id if move_ids_without_package.product_id.property_account_income_id
                        else move_ids_without_package.product_id.categ_id.property_account_income_categ_id.id,
                        'tax_ids': [(6, 0, [picking_id.company_id.account_purchase_tax_id.id])],
                        'quantity': move_ids_without_package.quantity_done,
                    })
                    invoice_line_list.append(vals)
                invoice = picking_id.env['account.move'].create({
                    'move_type': 'in_refund',
                    'invoice_origin': picking_id.name,
                    'invoice_user_id': current_user,
                    'narration': picking_id.name,
                    'partner_id': picking_id.partner_id.id,
                    'currency_id': picking_id.env.user.company_id.currency_id.id,
                    'journal_id': int(vendor_journal_id),
                    'payment_reference': picking_id.name,
                    'picking_id': picking_id.id,
                    'invoice_line_ids': invoice_line_list
                })
                return invoice

    def action_open_picking_invoice(self):
        """This is the function of the smart button which redirect to the
        invoice related to the current picking"""
        return {
            'name': 'Invoices',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'domain': [('invoice_origin', '=', self.name)],
            'context': {'create': False},
            'target': 'current'
        }


class StockReturnInvoicePicking(models.TransientModel):
    _inherit = 'stock.return.picking'

    def _create_returns(self):
        """in this function the picking is marked as return"""
        new_picking, pick_type_id = super(StockReturnInvoicePicking, self)._create_returns()
        picking = self.env['stock.picking'].browse(new_picking)
        picking.write({'is_return': True})
        return new_picking, pick_type_id
