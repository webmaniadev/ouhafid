# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _

class AccountPaymentRegisterInherit(models.TransientModel):
	_inherit = "account.payment.register"
	_description = "Payments Register"

	cheq_num = fields.Char(string="Number");
	cheq_img = fields.Binary(string="Image");

	def _create_payments(self):
		res = super(AccountPaymentRegisterInherit,self)._create_payments();
		res.write({"cheq_num" : self.cheq_num,
					"cheq_img" : self.cheq_img,});
		return res;


