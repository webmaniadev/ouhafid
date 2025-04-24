from odoo import models, fields, api, _


class Project(models.Model):
    _inherit = 'project.project'

    # Add a currency field if it doesn't exist already
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        related='company_id.currency_id',
        readonly=True
    )

    total_rg_invoiced = fields.Monetary(
        string='Total RG Facturé',
        compute='_compute_total_rg_invoiced',
        store=False,  # Not stored for simplicity
        help="Total des retenues de garantie facturées pour ce projet"
    )

    def _compute_total_rg_invoiced(self):
        for project in self:
            # Default value
            project.total_rg_invoiced = 0.0

            # Only proceed if there's an analytic account
            if not project.analytic_account_id:
                continue

            # Find sale orders with this analytic account
            sale_orders = self.env['sale.order'].search([
                ('analytic_account_id', '=', project.analytic_account_id.id)
            ])

            # If no sale orders, nothing to do
            if not sale_orders:
                continue

            # Collect all invoices
            invoices = self.env['account.move']
            for order in sale_orders:
                if hasattr(order, 'invoice_ids'):
                    # Only confirmed invoices, excluding RG invoices with ignore_cumul_rg flag
                    order_invoices = order.invoice_ids.filtered(
                        lambda inv: (
                                inv.state not in ('draft', 'cancel') and
                                not (hasattr(inv, 'ignore_cumul_rg') and inv.ignore_cumul_rg)
                        )
                    )
                    invoices |= order_invoices

            # If no invoices, nothing to do
            if not invoices:
                continue

            # Sort by creation date, newest first
            sorted_invoices = invoices.sorted(key=lambda inv: inv.create_date, reverse=True)

            # Track the total RG invoiced
            total_rg = 0.0

            # Check if the project has the required RG-related fields
            if not hasattr(sorted_invoices[0], 'cumul_rg'):
                # If cumul_rg doesn't exist, use an alternative method
                # Collect all RG invoices for this set of sale orders
                rg_invoices = sorted_invoices.filtered(
                    lambda inv: (
                            inv.is_rg_invoice and
                            not (hasattr(inv, 'ignore_cumul_rg') and inv.ignore_cumul_rg)
                    )
                )

                # Sum the RG invoice amounts
                if rg_invoices:
                    total_rg = sum(inv.amount_total for inv in rg_invoices)

                # If no RG-specific invoices found, try to find the RG amount from the latest invoice
                if total_rg == 0:
                    latest_invoice = sorted_invoices[0]

                    # Check if the latest invoice has a retenue_garantie or similar field
                    if hasattr(latest_invoice, 'retenue_garantie'):
                        total_rg = latest_invoice.retenue_garantie

            else:
                # Use cumul_rg if it exists, but filter out invoices with ignore_cumul_rg flag
                filtered_invoices = sorted_invoices.filtered(
                    lambda inv: not (hasattr(inv, 'ignore_cumul_rg') and inv.ignore_cumul_rg)
                )

                if filtered_invoices:
                    latest_invoice = filtered_invoices[0]
                    total_rg = latest_invoice.cumul_rg

            # Set the total RG invoiced
            project.total_rg_invoiced = total_rg