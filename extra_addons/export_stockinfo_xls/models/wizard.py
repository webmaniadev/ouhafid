# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2019-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author:Cybrosys Techno Solutions(odoo@cybrosys.com)
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

import time
from datetime import date, datetime
import pytz
import json
import datetime
import io
from odoo import api, fields, models, _
from odoo.tools import date_utils
try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter


class StockReport(models.TransientModel):
    _name = "wizard.stock.history"
    _description = "Current Stock History"


    def export_xls(self):
        data = {
            'ids': self.ids,
            'model': self._name,
            'warehouse': self.warehouse.ids,
            'category': self.category.ids,

        }
        return {
            'type': 'ir.actions.report',
            'data': {'model': 'wizard.stock.history',
                     'options': json.dumps(data, default=date_utils.json_default),
                     'output_format': 'xlsx',
                     'report_name': 'Indicateurs Analyse des ventes',
                     },
            'report_type': 'xlsx'
        }

    def get_warehouse(self, data):
        wh = data.warehouse.mapped('id')
        obj = self.env['stock.warehouse'].search([('id', 'in', wh)])
        l1 = []
        l2 = []
        for j in obj:
            l1.append(j.name)
            l2.append(j.id)
        return l1, l2

    warehouse = fields.Many2many(
        'stock.warehouse',
        'stock_wh_analysis_rel',
        'wizard_id',
        'warehouse_id',
        string='Warehouse',
        required=True
    )

    category = fields.Many2many(
        'product.category',
        'stock_categ_analysis_rel',
        'wizard_id',
        'category_id',
        string='Category'
    )

    date_from = fields.Date(string='Start Date')
    date_to = fields.Date(string='End Date')

    def get_lines(self, data, warehouse):
        lines = []

        pvp_values = []

        # Get all products
        domain = [('type', '=', 'product')]
        if data:
            domain += [('categ_id', 'in', data.mapped('id'))]

        products = self.env['product.product'].search(domain)

        products_by_ref = {}
        for product in products:
            ref = product.default_code or ''
            if ref not in products_by_ref:
                products_by_ref[ref] = []
            products_by_ref[ref].append(product)

        total_final_stock = 0
        total_valeur_achat_pro = 0
        total_ca_product = 0

        for ref, ref_products in products_by_ref.items():
            # Initialize aggregated values
            initial_stock = 0
            delivered_stock = 0
            total_valeur_achat = 0
            total_ca = 0
            point_mort = 0.0

            # Get first product's supplier
            first_product = ref_products[0]
            # frs = first_product.seller_ids and first_product.seller_ids[0].name.name or ''

            frs = ''
            for product in ref_products:
                if product.seller_ids:
                    frs = product.seller_ids[0].name.name  # Take the first supplier's name
                    break

            category = first_product.categ_id.name if first_product.categ_id else ''

            # Calculate initial stock using validated stock moves
            for product in ref_products:
                stock_move_domain = [
                    ('product_id', '=', product.id),
                    ('state', '=', 'done'),  # Only validated moves
                    ('location_dest_id.usage', '=', 'internal'),  # Incoming stock
                    ('location_id.usage', '!=', 'internal'),  # Exclude internal transfers
                    ('picking_type_id', '!=', 6)  # Exclude POS picking type
                ]
                inventory_moves = self.env['stock.move'].search(stock_move_domain)
                initial_stock += sum(move.quantity_done for move in inventory_moves)

            # Calculate delivered stock (outgoing stock)
            for product in ref_products:
                delivered_domain = [
                    ('state', '=', 'done'),
                    ('product_id', '=', product.id),
                    ('picking_id.picking_type_id.code', '=', 'outgoing')
                ]
                delivered_moves = self.env['stock.move.line'].search(delivered_domain)
                delivered_stock += sum(move.qty_done for move in delivered_moves)

            # Calculate final stock as the sum of qty_available for all products in the reference group
            final_stock = sum(
                product.with_context(warehouse=warehouse).qty_available
                for product in ref_products
            )

            # Other stock-related fields

            # Calculate sales values
            total_ca = (initial_stock - final_stock) * first_product.list_price
            total_valeur_achat = initial_stock * first_product.standard_price

            pvp_values.append(first_product.list_price)

            # Calculate margin and stock flow rate
            marge_moyenne = ((total_ca - total_valeur_achat) / total_valeur_achat) * 100 if total_valeur_achat > 0 else 0
            point_mort = max((total_valeur_achat - total_ca) / first_product.list_price, 0) if first_product.list_price else 0
            ecoulement_stock = ((initial_stock - final_stock) / initial_stock) * 100 if initial_stock > 0 else 0

            vals = {
                'frs': frs,
                'ref': ref,
                'category': category,  # Add category to the dictionary
                'si': initial_stock,
                'sf': final_stock,
                'cout_achat': first_product.standard_price,
                'pvp': first_product.list_price,
                'valeur_achat': total_valeur_achat,
                'ca': total_ca,
                'valeur_reste_pvp': final_stock * first_product.list_price,
                'valeur_reste_achat': final_stock * first_product.standard_price,
                'ecoulement_stock': int(round(ecoulement_stock, 0)),
                'point_mort': point_mort,
                'marge_moyenne': int(round(marge_moyenne, 0)),
            }

            lines.append(vals)

            total_final_stock += final_stock
            total_valeur_achat_pro += total_valeur_achat
            total_ca_product += total_ca

        total_pvp = (sum(pvp_values) / len(pvp_values)) * 0.7 if pvp_values else 0
        total_point_mort = max((total_valeur_achat_pro - total_ca_product) / total_pvp, 0) if total_pvp > 0 else 0
        lines.append({
            'frs': 'Total',
            'ref': '',
            'category': '',
            'si': '',
            'sf': total_final_stock,
            'cout_achat': '',
            'pvp': total_pvp,
            'valeur_achat': total_valeur_achat_pro,
            'ca': total_ca_product,
            'valeur_reste_pvp': '',
            'valeur_reste_achat': '',
            'ecoulement_stock': '',
            'point_mort': total_point_mort,
            'marge_moyenne': '',
        })
        return lines

    def get_xlsx_report(self, data, response):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet('Stock Analysis')

        # Formats
        header_format = workbook.add_format({
            'bold': True, 'align': 'center', 'bg_color': '#005f9e', 'font_color': 'white'
        })
        cell_format = workbook.add_format({'align': 'center', 'font_size': 10})
        number_format = workbook.add_format({'align': 'right', 'num_format': '#,##0'})
        float_format = workbook.add_format({'align': 'right', 'num_format': '#,##0.00'})
        percent_format = workbook.add_format({'align': 'right', 'num_format': '0%'})

        headers = [
            "Fournisseur", "Référence","Catégorie", "Stock Initial", "Stock Final",
            "Coût dAchat", "Prix de Vente", "Valeur dachat", "Chiffre d'affaires",
            "Valeur restante en stock En PVP", "Valeur restante en stock En Achat",
            "Ecoulement stock", "Point mort",
            "Marge moyenne"
        ]
        # Write headers
        for col, header in enumerate(headers):
            sheet.write(0, col, header, header_format)
            sheet.set_column(col, col, 20)

        # Fetch and write data
        lines = self.browse(data['ids'])
        warehouse_ids = lines.warehouse.mapped('id')

        row = 1
        for warehouse_id in warehouse_ids:
            for line in self.get_lines(lines.category, warehouse_id):
                sheet.write(row, 0, line['frs'], cell_format)
                sheet.write(row, 1, line['ref'], cell_format)
                sheet.write(row, 2, line['category'], cell_format)
                sheet.write(row, 3, line['si'], number_format)
                sheet.write(row, 4, line['sf'], number_format)
                sheet.write(row, 5, line['cout_achat'], number_format)
                sheet.write(row, 6, line['pvp'], number_format)
                sheet.write(row, 7, line['valeur_achat'], number_format)
                sheet.write(row, 8, line['ca'], number_format)
                sheet.write(row, 9, line['valeur_reste_pvp'], number_format)
                sheet.write(row, 10, line['valeur_reste_achat'], number_format)

                # Conditional formatting for stock flow rate
                #stock_flow_rate = line['ecoulement_stock'] / 100 if line['ecoulement_stock']
                stock_flow_rate = (
                    line['ecoulement_stock'] / 100
                    if isinstance(line['ecoulement_stock'], (int, float))
                    else ''
                )
                sheet.write(row, 11, stock_flow_rate, percent_format)


                sheet.write(row, 12, line['point_mort'], float_format)

                avg_margin = (
                        line['marge_moyenne'] / 100
                        if isinstance(line['marge_moyenne'], (int, float))
                        else ''
                )
                sheet.write(row, 13, avg_margin, percent_format)
                row += 1


        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()





