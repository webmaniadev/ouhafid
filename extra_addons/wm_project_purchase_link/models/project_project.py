# Copyright 2019 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import _, fields, models
from odoo.osv import expression
from odoo.tools.safe_eval import safe_eval


class ProjectProject(models.Model):
    _inherit = "project.project"

    purchase_count = fields.Integer(
        compute="_compute_purchase_info", string="# Purchase"
    )
    purchase_line_total = fields.Integer(
        compute="_compute_purchase_info", string="Purchase Total"
    )
    purchase_invoice_count = fields.Integer(
        compute="_compute_purchase_invoice_info", string="# Purchase Invoice"
    )
    purchase_invoice_line_total = fields.Float(
        compute="_compute_purchase_invoice_info", string="Purchase Invoice Total"
    )

    def _compute_purchase_info(self):
        for project in self:
            groups = self.env["purchase.order.line"].read_group(
                [
                    ("account_analytic_id", "=", project.analytic_account_id.id),
                    ("order_id.state", "!=", "cancel"),
                ],
                ["price_subtotal"],
                ["order_id"],
            )
            purchase_line_total = 0
            for group in groups:
                purchase_line_total += group["price_subtotal"]
            project.purchase_count = len(groups)
            project.purchase_line_total = purchase_line_total

    def _compute_purchase_invoice_info(self):
        for project in self:
            # Filter for purchase invoices (vendor bills) only
            # In Odoo 14, use move_type to distinguish invoice types
            domain = [
                ("analytic_account_id", "=", project.analytic_account_id.id),
                ("move_id.state", "!=", "cancel"),
                ("move_id.move_type", "in", ["in_invoice", "in_refund"]),  # Only vendor bills and refunds
            ]
            groups = self.env["account.move.line"].read_group(
                domain,
                ["price_subtotal"],
                ["move_id"],
            )
            purchase_invoice_line_total = 0
            for group in groups:
                purchase_invoice_line_total += group["price_subtotal"]
            project.purchase_invoice_count = len(groups)
            project.purchase_invoice_line_total = purchase_invoice_line_total

    def button_open_purchase_order(self):
        self.ensure_one()
        purchase_lines = self.env["purchase.order.line"].search(
            [("account_analytic_id", "in", self.mapped("analytic_account_id").ids)]
        )
        domain = [("id", "in", purchase_lines.mapped("order_id").ids)]
        return {
            "name": _("Purchase Order"),
            "domain": domain,
            "type": "ir.actions.act_window",
            "view_mode": "tree,form",
            "res_model": "purchase.order",
        }

    def button_open_purchase_order_line(self):
        self.ensure_one()
        domain = [("account_analytic_id", "in", self.mapped("analytic_account_id").ids)]
        return {
            "name": _("Purchase Order Lines"),
            "domain": domain,
            "type": "ir.actions.act_window",
            "view_mode": "tree,form",
            "res_model": "purchase.order.line",
        }

    def button_open_purchase_invoice(self):
        self.ensure_one()
        action = self.env.ref("account.action_move_in_invoice_type")
        action_dict = action.read()[0] if action else {}
        lines = self.env["account.move.line"].search(
            [
                ("analytic_account_id", "in", self.mapped("analytic_account_id").ids),
                ("move_id.move_type", "in", ["in_invoice", "in_refund"]),  # Only vendor bills and refunds
            ]
        )
        domain = expression.AND(
            [
                [("id", "in", lines.mapped("move_id").ids)],
                safe_eval(action.domain or "[]"),
            ]
        )
        action_dict.update({"domain": domain})
        return action_dict

    def button_open_purchase_invoice_line(self):
        self.ensure_one()
        domain = [
            ("analytic_account_id", "in", self.mapped("analytic_account_id").ids),
            ("move_id.move_type", "in", ["in_invoice", "in_refund"]),  # Only vendor bills and refunds
        ]
        return {
            "name": _("Purchase Invoice Lines"),
            "domain": domain,
            "type": "ir.actions.act_window",
            "view_mode": "tree,form",
            "res_model": "account.move.line",
        }
