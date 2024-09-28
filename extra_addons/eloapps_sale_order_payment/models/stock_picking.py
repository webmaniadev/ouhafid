from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from collections import defaultdict

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    price = fields.Integer(
    	string="Prix unitaire",
    	help="get price of product"
    	)
    
