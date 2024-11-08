# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api
import odoo.addons.decimal_precision as dp


class PosOrder(models.Model):
	_inherit = 'pos.order'
	margin = fields.Float(compute='_product_margin', digits=dp.get_precision('Product Price'), string="Margin",
						  store=True)

	@api.depends('lines.margin')
	def _product_margin(self):
		for order in self:
			order.margin = sum(order.lines.mapped('margin'))


class PosOrderLine(models.Model):
	_inherit = 'pos.order.line'

	purchase_price = fields.Float(string='Cost', compute='product_id_change_margin',
								  digits=dp.get_precision('Product Price'), store=True)
	margin = fields.Float(compute='_product_margin', digits=dp.get_precision('Product Price'), store=True)

	@api.depends('product_id')
	def product_id_change_margin(self):
		for line in self:
			line.purchase_price = line.product_id.standard_price
		return

	@api.depends('product_id', 'purchase_price', 'price_unit')
	def _product_margin(self):
		for line in self:
			line.margin = line.price_subtotal - (
					(line.purchase_price or line.product_id.standard_price) * line.qty)


class ResUsers(models.Model):
	_inherit = 'res.users'

	print_margin_show = fields.Boolean(string="Print Margin", compute='_default_show_margin', readonly=True)

	@api.depends('print_margin_show')
	def _default_show_margin(self):
		if self.env.user.has_group('bi_pos_margin.group_pos_margin'):
			self.print_margin_show = True
		else:
			self.print_margin_show = False


class ProductProduct(models.Model):
	_inherit = 'product.product'

	product_margin = fields.Float(string="Margin", compute='_compute_margin', store=True, readonly=True)

	@api.depends('list_price', 'standard_price')
	def _compute_margin(self):
		product_product = self.env['product.product'].search([])
		if len(product_product) > 0:
			for product1 in product_product:
				product1.write({
					'product_margin': product1.lst_price - product1.standard_price
				})


class ProductTemplate(models.Model):
	_inherit = 'product.template'

	bi_product_margin = fields.Float(string="Margin", compute='_bi_compute_margin', store=True, readonly=True)

	@api.depends('list_price', 'standard_price')
	def _bi_compute_margin(self):
		product_template = self.env['product.template'].search([])
		if len(product_template) > 0:
			for product in product_template:
				product.write({
					'bi_product_margin': product.list_price - product.standard_price
				})