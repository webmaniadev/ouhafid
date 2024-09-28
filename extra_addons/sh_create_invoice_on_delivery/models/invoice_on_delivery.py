# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.
from odoo import fields, models
from odoo.exceptions import UserError


class Picking(models.Model):
    _inherit = "stock.picking"
    # def write(self, vals):
    #     for rec in self:
    #         if vals.get('date_done') and rec.picking_type_code == 'outgoing':
    #             sale_orders = self.env['sale.order'].browse(
    #             self._context.get('active_ids', []))

    #             if self.env.user.has_group('sh_create_invoice_on_delivery.group_create_invoice_on_validate'):
    #                 invoice = sale_orders._create_invoices()
    #                 invoice.action_post()

    #                 if self.env.user.has_group('sh_create_invoice_on_delivery.group_auto_send_mail_on_validate'):

    #                     template_id = self.env.ref('account.email_template_edi_invoice')
    #                     template_id.with_context(model_description='').sudo().send_mail(invoice.id, force_send=True,notif_layout="mail.mail_notification_paynow")

    #             if self.env.user.has_group('sh_create_invoice_on_delivery.group_auto_send_mail_on_validate') and not  self.env.user.has_group('sh_create_invoice_on_delivery.group_create_invoice_on_validate'):
    #                 raise UserError("Please first enable 'Craete Invoice on stock validate' Configuration")

    #     return super(Picking, self).write(vals)
    sh_invoice_count = fields.Integer(compute="_compute_get_sh_invoice_count")

    def _compute_get_sh_invoice_count(self):
        invoice_coun_list = []
        get_invoices = self.env['account.move'].search([
            ('id', 'in', self.sale_id.invoice_ids.ids)
        ])
        for rec in get_invoices:
            if rec:
                invoice_coun_list.append(rec.id)
        self.sh_invoice_count = len(invoice_coun_list)

    def action_view_sh_invoice(self):
        return {
            "type": "ir.actions.act_window",
            "name": "Invoices",
            "view_mode": "tree,form",
            "res_model": "account.move",
            "domain": [('id', 'in', self.sale_id.invoice_ids.ids)],
        }

    def write(self, vals):
        res = super(Picking, self).write(vals)

        for rec in self:
            if vals.get('date_done') and rec.picking_type_code == 'outgoing':
                sale_orders = rec.sale_id
                if not sale_orders:
                    sale_orders = self.env['sale.order'].search([('picking_ids', 'in', rec.ids)])

                if rec.company_id.create_invoice:
                    if any(line for line in sale_orders.order_line if line.product_uom_qty != line.qty_invoiced):
                        invoice = sale_orders._create_invoices()
                        invoice.action_post()

                        if rec.company_id.auto_send_mail:
                            template_id = self.env.ref('account.email_template_edi_invoice')
                            template_id.with_context(model_description='').sudo().send_mail(
                                invoice.id,
                                force_send=True,
                                notif_layout="mail.mail_notification_paynow"
                            )

                if rec.company_id.auto_send_mail and not rec.company_id.create_invoice:
                    raise UserError("Please first enable 'Create Invoice on Delivery Validate' Configuration")

        return res
