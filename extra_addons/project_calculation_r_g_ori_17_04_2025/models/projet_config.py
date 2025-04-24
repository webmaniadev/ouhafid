# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    retention_guarantee_percentage = fields.Float(
        string='Pourcentage de retenue de garantie (%)',
        default=10.0,
        config_parameter='project.default_retention_percentage'
    )

    apply_retention_guarantee = fields.Boolean(
        string='Appliquer la retenue de garantie',
        default=False,
        config_parameter='project.apply_retention_guarantee'
    )