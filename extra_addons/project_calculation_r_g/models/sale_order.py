from odoo import models, fields, api, _
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    apply_rg_on_amount_total = fields.Boolean(
        string='Appliquer RG sur montant total',
        default=False,
        help="Si cochée, la garantie de rétention sera appliquée au montant total"
    )

    has_rg_invoiceable = fields.Boolean(
        string="Has RG to Invoice",
        compute="_compute_has_rg_invoiceable",
        store=True,
    )

    def _action_confirm(self):
        """Pass apply_rg_on_amount_total to pickings on confirmation"""
        result = super(SaleOrder, self)._action_confirm()

        # After confirmation,update the newly created pickings
        for picking in self.picking_ids:
            picking.apply_rg_on_amount_total = self.apply_rg_on_amount_total
        return result


    def action_print_bordereau_realise(self):
        """Print the bordereau réalisé based on the latest regular invoice"""
        self.ensure_one()

        # Get all posted invoices for this sale order that are NOT RG invoices
        regular_invoices = self.env['account.move'].search([
            ('invoice_origin', '=', self.name),
            ('state', '=', 'posted'),
            ('move_type', 'in', ['out_invoice', 'out_refund']),
            ('is_rg_invoice', '=', False)
        ], order='create_date desc, id desc')

        if not regular_invoices:
            raise UserError(
                _("No confirmed regular invoices found for this order. A confirmed invoice is required to generate the bordereau."))

        # Get the first invoice from the sorted list (the most recent one)
        latest_invoice = regular_invoices[0]

        # Return the report action directly using the report's action_report method
        return self.env.ref('project_calculation_r_g.action_report_bordereau_realise').report_action(latest_invoice)

    @api.depends('invoice_ids.state', 'invoice_ids.is_rg_invoice')
    def _compute_has_rg_invoiceable(self):
        for order in self:
            # Check for regular invoices to make sure we have at least one to get RG from
            regular_invoices = order.invoice_ids.filtered(lambda inv:
                                                          inv.state not in ('draft', 'cancel')
                                                          and not inv.is_rg_invoice)
            # Check if there's an RG invoice already
            existing_rg = order.invoice_ids.filtered(lambda inv: inv.is_rg_invoice)

            # Make RG button always visible as long as we don't have an RG invoice
            # and we're not in draft/cancel state and we have at least one regular invoice
            order.has_rg_invoiceable = (order.state not in ('draft', 'cancel')
                                        and bool(regular_invoices)
                                        and not existing_rg)

    def _nothing_to_invoice_error(self):
        # Override the original method to check if we can show the RG button instead
        if self.has_rg_invoiceable:
            return False  # Don't raise an error, we'll show the RG button instead

        msg = _("""There is nothing to invoice!
        Reason(s) of this behavior could be:
        - You should deliver your products before invoicing them.
        - You should modify the invoicing policy of your product: Open the product, go to the "Sales tab" and modify invoicing policy from "delivered quantities" to "ordered quantities".
        """)
        return UserError(msg)


    has_been_created = fields.Boolean(
        string="Has Been Created",
        compute="_compute_has_been_created",
    )
    def _compute_has_been_created(self):
        for order in self:
            # Find all stock pickings related to this sale order
            pickings = self.env['stock.picking'].search([
                ('origin', '=', order.name)
            ])

            # Check if ALL pickings are done
            all_pickings_done = bool(pickings) and all(p.state == 'done' for p in pickings)

            # Hide button if not all pickings are done (inverse of what we had before)
            order.has_bl_reserved = not all_pickings_done

    # In your sale.order model, add a computed field to check if RG invoice exists
    has_rg_invoice = fields.Boolean(
        string="Has RG Invoice",
        compute="_compute_has_rg_invoice",
        store=True,
        help="True if a retention guarantee invoice has been created for this order"
    )

    @api.depends('invoice_ids', 'invoice_ids.is_rg_invoice', 'invoice_ids.state')
    def _compute_has_rg_invoice(self):
        for order in self:
            # Check if there's any non-cancelled RG invoice
            order.has_rg_invoice = bool(order.invoice_ids.filtered(
                lambda inv: inv.is_rg_invoice and inv.state != 'cancel'
            ))

    def action_create_rg_invoice(self):
            """Create an invoice for the retention guarantee amount"""
            self.ensure_one()

            # Get the project related to this sale order
            project = False
            if self.analytic_account_id:
                project = self.env['project.project'].search([
                    ('analytic_account_id', '=', self.analytic_account_id.id)
                ], limit=1)

            if not project or not project.retenue_garantie:
                raise UserError(_("Aucun projet avec garantie de rétention trouvé pour cette commande."))

            # Get the retention guarantee amount directly from the project
            rg_amount = project.retenue_garantie
            rg_amount_ht = rg_amount / 1.2  # Convert to amount without tax (assuming 20% VAT)

            if not rg_amount_ht or rg_amount_ht <= 0:
                raise UserError(_("Le montant de la garantie de rétention est zéro ou n'est pas défini."))

            # Check if there's already an RG invoice
            existing_rg_invoices = self.invoice_ids.filtered(lambda inv: inv.is_rg_invoice and inv.state != 'cancel')
            if existing_rg_invoices:
                raise UserError(_("Une facture de garantie de rétention existe déjà pour cette commande."))

            # Prepare the invoice
            invoice_vals = self._prepare_invoice()
            invoice_vals['is_rg_invoice'] = True
            invoice_vals['invoice_origin'] = _("%s - Retention Guarantee") % self.name

            # Add a new flag to indicate this RG invoice should be ignored in cumul_rg calculations
            invoice_vals['ignore_cumul_rg'] = True

            # Create a dedicated RG product if it doesn't exist
            Product = self.env['product.product']
            rg_product = Product.search([('default_code', '=', 'RG'), ('type', '=', 'service')], limit=1)
            if not rg_product:
                rg_product = Product.create({
                    'name': _('Retention Guarantee'),
                    'default_code': 'RG',
                    'type': 'service',
                    'invoice_policy': 'order',
                    'uom_id': self.env.ref('uom.product_uom_unit').id,
                    'uom_po_id': self.env.ref('uom.product_uom_unit').id,
                })

            # Create a temporary sales order line for proper linking
            so_line = self.env['sale.order.line'].create({
                'order_id': self.id,
                'product_id': rg_product.id,
                'product_uom_qty': 1,
                'product_uom': rg_product.uom_id.id,
                'price_unit': 0,
                'name': _('Retention Guarantee Recovery'),
                'display_type': False,
                'qty_delivered': 1,  # Set as fully delivered
                'qty_invoiced': 0,
            })

            # Refresh the order to include the new line
            self.invalidate_cache()

            # Create the invoice with regular lines
            invoice_line_vals = [(0, 0, {
                'name': _('Retention Guarantee Recovery'),
                'product_id': rg_product.id,
                'price_unit': rg_amount_ht,  # Real amount on invoice
                'quantity': 1.0,
                'product_uom_id': rg_product.uom_id.id,
                'tax_ids': [(6, 0, so_line.tax_id.ids)],
                'sale_line_ids': [(6, 0, [so_line.id])],  # Link to the SO line
                'exclude_from_invoice_tab': False,
                'analytic_account_id': self.analytic_account_id.id if self.analytic_account_id else False,
            })]

            invoice_vals['invoice_line_ids'] = invoice_line_vals
            invoice = self.env['account.move'].create(invoice_vals)

            # Update the SO line with the invoice line reference
            so_line.write({
                'invoice_lines': [(4, line.id) for line in invoice.invoice_line_ids],
                'qty_invoiced': 1,  # Mark as fully invoiced
            })

            # Set the custom field montant_rg_du to the RG amount
            invoice.write({
                'retenue_garantie': 0.0,  # Set RG to 0 for this invoice
            })

            # Force a refresh of the invoice counter and related fields
            self.env['account.move'].flush()
            self.env['sale.order'].flush()
            self.env['sale.order.line'].flush()
            self.invalidate_cache()

            # Manually link the invoice to the sale order in both directions
            if invoice.id not in self.invoice_ids.ids:
                # Add this invoice to the sale order's invoices through the many2many relation
                self.message_post(
                    body=_("Retention Guarantee Invoice %s created", invoice.name),
                    subtype_xmlid='mail.mt_note'
                )
                # Create a proper invoice-to-order link in Odoo
                self.write({'invoice_ids': [(4, invoice.id)]})
                invoice.write({'invoice_origin': self.name})

            # Redirect to the invoice
            return {
                'name': _('Retention Guarantee Invoice'),
                'type': 'ir.actions.act_window',
                'res_model': 'account.move',
                'res_id': invoice.id,
                'view_mode': 'form',
                'target': 'current',
            }
