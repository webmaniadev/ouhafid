# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ProjectProject(models.Model):
    _inherit = 'project.project'

    caution_provisoire = fields.Monetary(
        string='Caution provisoire',
        currency_field='currency_id',
        required=True,
    )

    caution_definitif = fields.Monetary(
        string='Caution définitive',
        currency_field='currency_id',
        required=True,
    )

    retenue_garantie = fields.Monetary(
        string='Retenue de garantie',
        currency_field='currency_id',
        required=True,
    )

    # Adding currency field (required for monetary fields)
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: self.env.ref('base.MAD'),  # Set Moroccan Dirham as default
        required=True
    )



    # Adding SQL constraint for unique project name
    _sql_constraints = [
        ('unique_project_name',
         'UNIQUE(name)',
         _('Le nom du projet doit être unique!'))
    ]

    @api.constrains('name')
    def _check_unique_name(self):
        for record in self:
            if record.name:
                domain = [('name', '=', record.name)]
                if record.id:
                    domain.append(('id', '!=', record.id))
                if self.search_count(domain):
                    raise ValidationError(_('Un projet avec ce nom existe déjà !'))
