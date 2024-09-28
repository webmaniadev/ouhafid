
from odoo import models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'

    phone = fields.Char(required=True)
    email = fields.Char(required=True)
