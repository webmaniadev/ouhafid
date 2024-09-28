# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _

class AccountPaymentInherit(models.Model):
	_inherit = "account.payment"
	_description = "Payments"

	cheq_num = fields.Char(string="Number");
	cheq_img = fields.Binary(string="Image");




	




