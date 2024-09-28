from odoo import models, fields, api, _
from odoo.exceptions import UserError
import inspect
from collections import defaultdict


class AccountMove(models.Model):
    _inherit = 'account.move'
