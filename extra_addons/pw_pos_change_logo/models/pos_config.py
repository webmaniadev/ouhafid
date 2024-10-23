# -*- coding: utf-8 -*-

from odoo import api, models, fields, _

class PosConfig(models.Model):
    _inherit = 'pos.config'

    pw_change_logo = fields.Boolean('Change Logo')
    pw_pos_logo = fields.Binary(string="POS Logo")
