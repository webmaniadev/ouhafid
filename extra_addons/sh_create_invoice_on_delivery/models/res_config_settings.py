# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    create_invoice = fields.Boolean(string="Create Invoice on Delivery Validate")
    auto_send_mail = fields.Boolean(string="Send Invoice to Customer on Delivery Validate")


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    create_invoice = fields.Boolean(
        string="Create Invoice on Delivery Validate", related="company_id.create_invoice", readonly=False)
    auto_send_mail = fields.Boolean(
        string="Send Invoice to Customer on Delivery Validate", related="company_id.auto_send_mail", readonly=False)
