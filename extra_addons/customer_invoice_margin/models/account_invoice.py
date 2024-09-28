# -*- coding: utf-8 -*-
#################################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2021-today Ascetic Business Solution <www.asceticbs.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#################################################################################

from odoo import api, models, fields


class AccountMove(models.Model):
    _inherit = "account.move"
    pricelist_id = fields.Many2one('product.pricelist', string='Pricelist')

    margin_amount = fields.Char(compute='_get_average_margin_percentage', string='Margin Amount')
    margin_percentage = fields.Char(compute='_get_average_margin_percentage', string='Margin Percentage')

    @api.depends('invoice_line_ids', 'invoice_line_ids.quantity', 'invoice_line_ids.price_unit',
                 'invoice_line_ids.discount', 'invoice_line_ids.price_subtotal', 'invoice_line_ids.margin_amount')
    def _get_average_margin_percentage(self):
        sale_price = discount = cost = margin_amount = 0.0
        line_cost = line_margin_amount = margin_percentage = amount_untaxed_without_discount = 0.0
        for record in self:
            line_margin_amount = sum(record.line_ids.filtered(lambda line: line.product_id).mapped('margin_amount'))
            print(line_margin_amount)
            if record.invoice_line_ids:
                for line in record.invoice_line_ids:
                    exclude_product = False
                    pricelist_id = record.pricelist_id
                    pricelist_items = self.env['product.pricelist.item'].search(
                        [('pricelist_id', '=', pricelist_id.id),
                         ('product_tmpl_id', '=', line.product_id.product_tmpl_id.id),
                         ('date_start', '<=', record.invoice_date),
                         '|', ('date_end', '>=', record.invoice_date), ('date_end', '=', False)
                         ])
                    if pricelist_items:
                        exclude_product = any(item.exclude_product_test for item in pricelist_items)
                    if exclude_product:
                        amount_untaxed_without_discount += line.price_unit / (1 + 0.2) * line.quantity
                    else:
                        amount_untaxed_without_discount += line.price_subtotal

                    margin_percentage = amount_untaxed_without_discount and line_margin_amount / amount_untaxed_without_discount * 100

                    record.margin_amount = str(round(line_margin_amount, 2)) + "DH"
                    record.margin_percentage = str(round(margin_percentage, 2)) + "%"
            else:
                record.margin_amount = ' '
                record.margin_percentage = ' '


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    margin_percentage = fields.Char(compute='_get_total_percentage', string='Margin Percentage')
    margin_amount = fields.Float(compute='_get_total_percentage', string='Margin Amount')
    exclude_product = fields.Boolean(compute='_compute_exclude_product', store=True)

    @api.depends('quantity', 'price_unit', 'discount', 'price_subtotal', 'product_id', 'move_id.invoice_date',
                 'move_id.currency_id')
    def _get_total_percentage(self):
        sale_price = discount = cost = margin_amount = margin_percentage = 0.0
        for record in self:
            if record.product_id:
                exclude_product = record.exclude_product
                if exclude_product:
                    subtotal_without_discount = record.price_unit / (1 + 0.2) * record.quantity
                    margin = subtotal_without_discount - (record.product_id.standard_price * record.quantity)
                    margin_percente = (margin / subtotal_without_discount) * 100 if subtotal_without_discount != 0 else 0

                else:
                    margin = record.price_subtotal - (record.product_id.standard_price * record.quantity)
                    margin_percente = (margin / record.price_subtotal) * 100 if record.price_subtotal != 0 else 0

                record.margin_amount = margin
                record.margin_percentage = str(round(margin_percente, 2)) + '%'
            else:
                record.margin_percentage = 0
                record.margin_amount = 0

    @api.depends('product_id', 'move_id.pricelist_id', 'move_id.invoice_date')
    def _compute_exclude_product(self):
        for line in self:
            exclude_product = True
            pricelist_items = self.env['product.pricelist.item'].search(
                [('pricelist_id', '=', line.move_id.pricelist_id.id),
                 ('product_tmpl_id', '=', line.product_id.product_tmpl_id.id),
                 ('date_start', '<=', line.move_id.invoice_date),
                 '|', ('date_end', '>=', line.move_id.invoice_date), ('date_end', '=', False)
                 ])
            if pricelist_items:
                if line.product_id:
                    exclude_product = any(item.exclude_product_test for item in pricelist_items)
                else:
                    exclude_product = False

            line.exclude_product = exclude_product


class PricelistItem(models.Model):
    _inherit = 'product.pricelist.item'
    exclude_product_test = fields.Boolean(string="Exclude Product")
