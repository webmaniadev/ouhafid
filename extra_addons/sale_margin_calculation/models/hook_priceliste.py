from odoo import models, fields, api


class Product(models.Model):
    _inherit = "product.pricelist.item"
    exclude_product_test = fields.Boolean(string="Inclue Article")
