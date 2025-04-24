# Copyright 2025 Your Name
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import _, fields, models
from odoo.osv import expression
from odoo.tools.safe_eval import safe_eval


class ProjectProject(models.Model):
    _inherit = "project.project"

    # Fields for HR Expenses
    expense_count = fields.Integer(
        compute="_compute_expense_info", string="# Expenses"
    )
    expense_total = fields.Float(
        compute="_compute_expense_info", string="Expenses Total"
    )
    expense_sheet_count = fields.Integer(
        compute="_compute_expense_sheet_info", string="# Expense Reports"
    )
    expense_sheet_total = fields.Float(
        compute="_compute_expense_sheet_info", string="Expense Reports Total"
    )

    def _compute_expense_info(self):
        for project in self:
            expenses = self.env['hr.expense'].search([
                ('analytic_account_id', '=', project.analytic_account_id.id),
                ('state', 'in', ['approved', 'done']),
            ])

            project.expense_count = len(expenses)
            project.expense_total = sum(expenses.mapped('total_amount'))

    def _compute_expense_sheet_info(self):
        for project in self:
            # First find all expenses linked to this analytic account
            expenses = self.env['hr.expense'].search([
                ('analytic_account_id', '=', project.analytic_account_id.id),
                ('state', 'in', ['approved', 'done']),
            ])

            # Then get the unique expense sheets (reports) from those expenses
            expense_sheets = expenses.mapped('sheet_id')

            project.expense_sheet_count = len(expense_sheets)
            project.expense_sheet_total = sum(expense_sheets.mapped('total_amount'))

    def button_open_expenses(self):
        self.ensure_one()
        domain = [
            ('analytic_account_id', 'in', self.mapped('analytic_account_id').ids),
            ('state', 'in', ['approved', 'done']),
        ]
        return {
            "name": _("Expenses"),
            "domain": domain,
            "type": "ir.actions.act_window",
            "view_mode": "tree,form",
            "res_model": "hr.expense",
        }

    def button_open_expense_sheets(self):
        self.ensure_one()
        # First find expenses with this analytic account
        expenses = self.env['hr.expense'].search([
            ('analytic_account_id', 'in', self.mapped('analytic_account_id').ids),
            ('state', 'in', ['approved', 'done']),
        ])

        # Then get the expense sheets
        expense_sheet_ids = expenses.mapped('sheet_id').ids

        domain = [('id', 'in', expense_sheet_ids)]
        return {
            "name": _("Expense Reports"),
            "domain": domain,
            "type": "ir.actions.act_window",
            "view_mode": "tree,form",
            "res_model": "hr.expense.sheet",
        }