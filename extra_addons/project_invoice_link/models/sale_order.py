# Copyright 2025 Your Name
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import _, fields, models
from odoo.osv import expression
from odoo.tools.safe_eval import safe_eval


class ProjectProject(models.Model):
    _inherit = "project.project"

    # Fields for Sale Orders
    sale_count = fields.Integer(
        compute="_compute_sale_info", string="# Sales"
    )
    sale_line_total = fields.Float(
        compute="_compute_sale_info", string="Sales Total"
    )
    # Fields for Sale Invoices
    sale_invoice_count = fields.Integer(
        compute="_compute_sale_invoice_info", string="# Sales Invoice"
    )
    sale_invoice_line_total = fields.Float(
        compute="_compute_sale_invoice_info", string="Sales Invoice Total"
    )

    def _compute_sale_info(self):
        for project in self:
            # In Odoo 14, we need to look at the order itself for the analytic account
            orders = self.env['sale.order'].search([
                ('analytic_account_id', '=', project.analytic_account_id.id),
                ('state', '!=', 'cancel'),
            ])

            project.sale_count = len(orders)

            # Get total from the sale order lines
            sale_line_total = 0.0
            for order in orders:
                for line in order.order_line:
                    sale_line_total += line.price_subtotal

            project.sale_line_total = sale_line_total

    def _compute_sale_invoice_info(self):
        for project in self:
            domain = [
                ("analytic_account_id", "=", project.analytic_account_id.id),
                ("move_id.state", "!=", "cancel"),
                ("move_id.move_type", "in", ["out_invoice", "out_refund"]),
            ]
            groups = self.env["account.move.line"].read_group(
                domain,
                ["price_subtotal"],
                ["move_id"],
            )
            sale_invoice_line_total = 0.0
            for group in groups:
                sale_invoice_line_total += group["price_subtotal"]
            project.sale_invoice_count = len(groups)
            project.sale_invoice_line_total = sale_invoice_line_total

    def button_open_sale_order(self):
        self.ensure_one()
        domain = [
            ("analytic_account_id", "in", self.mapped("analytic_account_id").ids),
            ("state", "!=", "cancel"),
        ]
        return {
            "name": _("Sale Orders"),
            "domain": domain,
            "type": "ir.actions.act_window",
            "view_mode": "tree,form",
            "res_model": "sale.order",
        }

    def button_open_sale_order_line(self):
        self.ensure_one()
        orders = self.env["sale.order"].search([
            ("analytic_account_id", "in", self.mapped("analytic_account_id").ids),
            ("state", "!=", "cancel"),
        ])
        domain = [("order_id", "in", orders.ids)]
        return {
            "name": _("Sale Order Lines"),
            "domain": domain,
            "type": "ir.actions.act_window",
            "view_mode": "tree,form",
            "res_model": "sale.order.line",
        }

    def button_open_sale_invoice(self):
        self.ensure_one()
        action = self.env.ref("account.action_move_out_invoice_type")
        action_dict = action.read()[0] if action else {}
        lines = self.env["account.move.line"].search(
            [
                ("analytic_account_id", "in", self.mapped("analytic_account_id").ids),
                ("move_id.move_type", "in", ["out_invoice", "out_refund"]),
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

