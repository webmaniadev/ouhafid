# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools


class PosOrderReport(models.Model):
	_inherit = "report.pos.order"

	margin = fields.Float(string='Total Margin / Total Profit')
	cost_price_total = fields.Float(string='Cost Price Total')
	cost_price_unit = fields.Float(string='Cost Price/Unit')
	profit_sale_price = fields.Float(string='Margin / Profit(Sale Price-Cost Price)')
	

	def _select(self):

		return super(PosOrderReport, self)._select() +',SUM(l.margin) AS margin,SUM(l.qty * l.purchase_price) AS cost_price_total,SUM(l.purchase_price / CASE COALESCE(s.currency_rate, 0) WHEN 0 THEN 1.0 ELSE s.currency_rate END) AS cost_price_unit,SUM(l.price_unit - l.purchase_price) AS profit_sale_price'

