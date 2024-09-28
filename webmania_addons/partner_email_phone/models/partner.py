from odoo import models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'

    phone = fields.Char(required=True)
    email = fields.Char(required=True)
    mobile = fields.Char(required=True)
    street = fields.Char(required=True)
    city = fields.Char(required=True)
    country_id = fields.Many2one('res.country', string='Country', required=True)
    zip = fields.Char(required=True)
