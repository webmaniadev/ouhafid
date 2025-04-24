# -*- coding: utf-8 -*-

from odoo import models, fields, api

class AccountMove(models.Model):
    _inherit = 'account.move'

    # Add this field to your AccountMove model
    potential_rg_cum = fields.Monetary(
        string='Potential RG from Cumul',
        currency_field='currency_id',
        compute='_compute_potential_rg_cum',
        store=True
    )
    ignore_cumul_rg = fields.Boolean(
        string='Ignore in Cumul RG Calculations',
        default=False
    )
    is_rg_invoice = fields.Boolean(
        string="Is Retention Guarantee Invoice",
        default=False,
        help="Indicates that this invoice is for a retention guarantee",
    )

    # rg 7% de marche
    retenue_garantie = fields.Monetary(
        string='Montant de la R.G  7% du marché TTC',
        currency_field='currency_id',
        compute='_compute_retenue_garantie',
        store=True
    )
    cumul_rg = fields.Monetary(
        string='Total des RG',
        currency_field='currency_id',
        compute='_compute_retenue_garantie',
        store=True
    )
    calculated_rg = fields.Monetary(
        string='Montant de la R.G  TTC  ',
        currency_field='currency_id',
        compute='_compute_retenue_garantie',
        store=True
    )
    rg_report = fields.Monetary(
        string='RG 7% ',
        currency_field='currency_id',
        compute='_compute_retenue_garantie',
        store=True
    )
    montant_rg_du = fields.Monetary(
        string='Net à payer TTC',
        currency_field='currency_id',
        compute='_compute_retenue_garantie',
        store=True
    )
    cumulative_subtotal = fields.Monetary(
        string='Cumulative Subtotal',
        compute='_compute_cumulative_totals',
        store=True,
        currency_field='currency_id'
    )

    cumulative_tax = fields.Monetary(
        string='Cumulative Tax',
        compute='_compute_cumulative_totals',
        store=True,
        currency_field='currency_id'
    )

    cumulative_total = fields.Monetary(
        string='Cumulative Total',
        compute='_compute_cumulative_totals',
        store=True,
        currency_field='currency_id'
    )
    total_facture_ttc = fields.Monetary(
        string='Total Facture TTC',
        compute='_compute_previous_totals',
        store=True,
        currency_field='currency_id'
    )

    previous_invoice_total = fields.Monetary(
        string='Previous Invoice Total',
        compute='_compute_previous_totals',
        store=True,
        currency_field='currency_id'
    )

    has_previous_invoice = fields.Boolean(
        string='Has Previous Invoice',
        compute='_compute_previous_totals',
        store=True
    )
    # Add this field to your AccountMove model
    is_max_rg = fields.Boolean(
        string='Is Maximum RG',
        compute='_compute_is_max_rg',
        store=True
    )
    has_project = fields.Boolean(
        string="Has Related Project",
        compute="_compute_has_project",
        store=True
    )

    @api.depends('invoice_origin', 'line_ids.analytic_account_id')
    def _compute_has_project(self):
        for move in self:
            # Check if any invoice line has an analytic account
            if move.line_ids.filtered(lambda l: l.analytic_account_id):
                move.has_project = True
            # Or check if it's related to a sale order with a project
            elif move.invoice_origin:
                sale_order = self.env['sale.order'].search([('name', '=', move.invoice_origin)], limit=1)
                move.has_project = bool(sale_order and sale_order.analytic_account_id)
            else:
                move.has_project = False

    @api.depends('rg_report', 'retenue_garantie')
    def _compute_is_max_rg(self):
        for move in self:
            move.is_max_rg = move.rg_report == move.retenue_garantie and move.retenue_garantie > 0

    def _compute_amount(self):
        result = super(AccountMove, self)._compute_amount()

        # Don't calculate retenue_garantie for RG invoices
        for move in self:
            if move.is_rg_invoice:
                move.retenue_garantie = 0.0

        return result
    @api.depends('cumulative_total')
    def _compute_potential_rg_cum(self):
        for move in self:
            # Calculate 10% of cumulative total
            retention_percentage = move._get_retention_percentage()
            move.potential_rg_cum = move.cumulative_total * (retention_percentage / 100.0)


    @api.depends('invoice_line_ids.cumulative_price')
    def _compute_cumulative_totals(self):
        for move in self:
            # Get current invoice lines total
            move.cumulative_subtotal = sum(move.invoice_line_ids.mapped('cumulative_price'))

            # Skip if the move has a temporary ID (not yet saved to database)
            if not move.id or isinstance(move.id, models.NewId):
                move.cumulative_tax = 0.0
                move.cumulative_total = move.cumulative_subtotal
                continue

            # Add lines from previous invoices that aren't in current invoice
            if move.invoice_origin:
                sale_order = self.env['sale.order'].search([
                    ('name', '=', move.invoice_origin)
                ], limit=1)

                if sale_order:
                    # Get all products in current invoice
                    current_products = set(move.invoice_line_ids.mapped('product_id.id'))

                    # Get all previous invoices
                    all_invoices = self.env['account.move'].search([
                        ('invoice_origin', '=', move.invoice_origin),
                        ('id', '!=', move.id),
                        ('state', '!=', 'cancel'),
                        ('move_type', 'in', ['out_invoice', 'out_refund'])
                    ])

                    # Go through sale order lines for products not in current invoice
                    for so_line in sale_order.order_line:
                        if so_line.product_id and so_line.product_id.id not in current_products:
                            previous_qty = 0.0

                            # Calculate previously invoiced quantity for this product
                            for inv in all_invoices:
                                for inv_line in inv.invoice_line_ids:
                                    if inv_line.product_id and inv_line.product_id.id == so_line.product_id.id:
                                        previous_qty += inv_line.quantity

                            # Only include if product has been previously invoiced
                            if previous_qty > 0:
                                # Calculate price with discount
                                price = so_line.price_unit * previous_qty
                                if so_line.discount:
                                    price = price * (1 - (so_line.discount / 100.0))

                                # Add to cumulative subtotal
                                move.cumulative_subtotal += price

            # Calculate tax on cumulative subtotal
            if move.amount_untaxed:
                tax_ratio = move.amount_tax / move.amount_untaxed
                move.cumulative_tax = move.cumulative_subtotal * tax_ratio
            else:
                move.cumulative_tax = 0.0

            move.cumulative_total = move.cumulative_subtotal + move.cumulative_tax

            # Debug output
            print(f"Invoice {move.name}: Cumulative total calculated: {move.cumulative_total}")

    @api.depends('analytic_account_id', 'montant_rg_du', 'amount_total')
    def _compute_display_amount(self):
        for move in self:
            move.display_amount = move.montant_rg_du if move.analytic_account_id else move.amount_total

    @api.depends('cumulative_total', 'rg_report', 'retenue_garantie', 'invoice_origin', 'state')
    def _compute_previous_totals(self):
        for move in self:
            # Default values
            move.previous_invoice_total = 0.0
            move.has_previous_invoice = False

            # Calculate total facture TTC using cumulative_total instead of amount_total
            # This is the key change you requested - using cumulative values
            move.total_facture_ttc = move.cumulative_total - move.rg_report

            #move.total_facture_ttc = move.cumulative_total - move.rg_report


            # Default net_a_payer is the same as total_facture_ttc for first invoices

            # Skip if the move has a temporary ID (not yet saved to database)
            if not move.id or isinstance(move.id, models.NewId) or move.move_type not in ('out_invoice', 'out_refund') or not move.invoice_origin:
                continue

            if move.move_type not in ('out_invoice', 'out_refund') or not move.invoice_origin:
                continue

            # Find previous invoices for the same origin
            previous_invoices = self.env['account.move'].search([
                ('invoice_origin', '=', move.invoice_origin),
                ('id', '!=', move.id),
                ('state', '=', 'posted'),  # Only consider posted invoices
                ('move_type', 'in', ['out_invoice', 'out_refund']),
                ('create_date', '<', move.create_date)
            ], order='create_date desc', limit=1)  # Get the most recent

            if previous_invoices:
                # Get previous invoice's total after RG
                prev_inv = previous_invoices[0]

                # Check which RG value is being used
                if move.rg_report == move.potential_rg_cum:
                    # If using percentage of cumulative total, sum all previous montant_rg_du
                    previous_montant_rg_du_total = 0.0
                    all_prev_invoices = self.env['account.move'].search([
                        ('invoice_origin', '=', move.invoice_origin),
                        ('id', '!=', move.id),
                        ('state', '!=', 'cancel'),
                        ('move_type', 'in', ['out_invoice', 'out_refund']),
                        ('create_date', '<', move.create_date)
                    ])

                    for prev in all_prev_invoices:
                        previous_montant_rg_du_total += prev.montant_rg_du

                    # Set previous_invoice_total to the sum of all previous montant_rg_du
                    move.previous_invoice_total = previous_montant_rg_du_total
                else:
                    # Otherwise, use the previous invoice's total_facture_ttc
                    move.previous_invoice_total = prev_inv.total_facture_ttc

                move.has_previous_invoice = True



    def _get_retention_percentage(self):
        """Get retention guarantee percentage from config"""
        config_param = self.env['ir.config_parameter'].sudo()
        return float(config_param.get_param('project.default_retention_percentage', 10.0))

    @api.depends('invoice_line_ids', 'amount_total')
    def _compute_retenue_garantie(self):
        for move in self:
            # Skip computation for new records (temporary IDs)
            if not move.id or isinstance(move.id, str):
                move.retenue_garantie = 0.0
                move.calculated_rg = 0.0
                move.montant_rg_du = 0.0
                move.cumul_rg = 0.0
                move.rg_report = 0.0
                continue

            sale_order = self.env['sale.order'].search([
                ('name', '=', move.invoice_origin)
            ], limit=1)

            if sale_order and sale_order.analytic_account_id:
                project = self.env['project.project'].search([
                    ('analytic_account_id', '=', sale_order.analytic_account_id.id)
                ], limit=1)

                if project and project.retenue_garantie:
                    # Get previous RG total for this project
                    previous_invoices = self.env['account.move'].search([
                        ('invoice_origin', '!=', False),
                        ('id', '!=', move.id),
                        ('state', '!=', 'cancel'),
                        ('move_type', 'in', ['out_invoice', 'out_refund'])
                    ])

                    previous_rg_total = 0.0
                    for inv in previous_invoices:
                        inv_sale_order = self.env['sale.order'].search([
                            ('name', '=', inv.invoice_origin)
                        ], limit=1)
                        if inv_sale_order and inv_sale_order.analytic_account_id == project.analytic_account_id:
                            previous_rg_total += inv.calculated_rg

                    # Calculate potential RG for current invoice
                    retention_percentage = self._get_retention_percentage()
                    potential_rg = move.amount_total * (retention_percentage / 100.0)

                    move.retenue_garantie = project.retenue_garantie

                    # Check if adding potential RG would exceed the total retention limit
                    if previous_rg_total + potential_rg <= move.retenue_garantie:
                        # If not exceeding, use the full percentage
                        move.calculated_rg = potential_rg
                        #add variable name it rg_report
                        #move.rg_report = move.calculated_rg

                    else:
                        # If exceeding, only use the remaining available amount
                        move.calculated_rg = max(0, move.retenue_garantie - previous_rg_total)
                        #move.rg_report = move.retenue_garantie

                    # Update cumulative RG and amount due
                        # For rg_report, compare potential_rg_cum with retenue_garantie
                    if move.potential_rg_cum > move.retenue_garantie:
                        move.rg_report = move.retenue_garantie
                    else:
                        move.rg_report = move.potential_rg_cum

                    move.cumul_rg = previous_rg_total + move.calculated_rg
                    move.montant_rg_du = move.amount_total - move.calculated_rg
                else:
                    move.retenue_garantie = 0.0
                    move.calculated_rg = 0.0
                    move.montant_rg_du = 0.0
                    move.cumul_rg = 0.0
            else:
                move.retenue_garantie = 0.0
                move.calculated_rg = 0.0
                move.montant_rg_du = 0.0
                move.cumul_rg = 0.0





    # report Excel cumulation
    def _get_previous_quantity(self, current_line):
        """
        Calculate the total quantity of a product from previous invoices for the same project
        """
        self.ensure_one()
        if not self.invoice_origin:
            return 0.0

        sale_order = self.env['sale.order'].search([
            ('name', '=', self.invoice_origin)
        ], limit=1)

        if not sale_order or not sale_order.analytic_account_id:
            return 0.0

        # Get the project
        project = self.env['project.project'].search([
            ('analytic_account_id', '=', sale_order.analytic_account_id.id)
        ], limit=1)

        if not project:
            return 0.0

        # Get previous invoices for the same project
        previous_invoices = self.env['account.move'].search([
            ('invoice_origin', '!=', False),
            ('id', '!=', self.id),
            ('state', '!=', 'cancel'),
            ('move_type', 'in', ['out_invoice', 'out_refund']),
            ('create_date', '<', self.create_date or fields.Date.today())
        ])

        previous_quantity = 0.0
        for invoice in previous_invoices:
            inv_sale_order = self.env['sale.order'].search([
                ('name', '=', invoice.invoice_origin)
            ], limit=1)

            if inv_sale_order and inv_sale_order.analytic_account_id == project.analytic_account_id:
                # Find lines with the same product
                for line in invoice.invoice_line_ids:
                    if line.product_id == current_line.product_id:
                        previous_quantity += line.quantity

        return previous_quantity


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    previous_quantity = fields.Float(
        string='Previous Quantity',
        compute='_compute_cumulative_quantities',
        store=True,
        digits='Product Unit of Measure'
    )

    cumulative_quantity = fields.Float(
        string='Cumulative Quantity',
        compute='_compute_cumulative_quantities',
        store=True,
        digits='Product Unit of Measure'
    )

    cumulative_price = fields.Monetary(
        string='Cumulative Price',
        compute='_compute_cumulative_quantities',
        store=True,
        currency_field='currency_id'
    )

    # This field indicates if this is a "virtual" line for a product not in current invoice
    is_virtual_line = fields.Boolean(
        string='Virtual Line',
        default=False,
        help="True if this line represents a product from previous invoices not in current invoice"
    )

    @api.depends('move_id', 'product_id', 'quantity', 'price_unit', 'move_id.state')
    def _compute_cumulative_quantities(self):
        for line in self:
            line.previous_quantity = 0.0
            line.cumulative_quantity = line.quantity
            line.cumulative_price = line.price_subtotal

            # Skip non-customer invoices
            if line.move_id.move_type not in ('out_invoice', 'out_refund'):
                continue

            # Skip if no origin or product
            if not line.move_id.invoice_origin or not line.product_id:
                continue

            # Skip if the move has a temporary ID (not yet saved to database)
            if not line.move_id.id or isinstance(line.move_id.id, models.NewId):
                continue

            # If the invoice is already posted/confirmed, don't recalculate previous_quantity
            if line.move_id.state == 'posted' and hasattr(line, 'previous_quantity') and line.previous_quantity != 0.0:
                # Keep the existing previous_quantity value
                prev_qty = line.previous_quantity

                # Only recalculate cumulative quantity
                cumul_qty = prev_qty + line.quantity

                # Check delivered quantity if there's a sale order origin
                if line.move_id.invoice_origin:
                    sale_order = self.env['sale.order'].search([
                        ('name', '=', line.move_id.invoice_origin)
                    ], limit=1)

                    if sale_order and line.product_id:
                        delivered_qty = self._get_delivered_quantity(sale_order, line.product_id)
                        if delivered_qty > 0 and cumul_qty > delivered_qty:
                            cumul_qty = delivered_qty

                line.cumulative_quantity = cumul_qty

                # Calculate cumulative price
                line.cumulative_price = line.price_unit * cumul_qty
                # Apply discount if any
                if line.discount:
                    line.cumulative_price = line.cumulative_price * (1 - (line.discount / 100.0))
                continue

            # Initialize values
            line.previous_quantity = 0.0
            line.cumulative_quantity = line.quantity
            line.cumulative_price = line.price_subtotal

            # Skip non-customer invoices
            if line.move_id.move_type not in ('out_invoice', 'out_refund'):
                continue

            # Skip if no origin or product
            if not line.move_id.invoice_origin or not line.product_id:
                continue

            # Get the sale order related to this invoice
            current_sale_order = self.env['sale.order'].search([
                ('name', '=', line.move_id.invoice_origin)
            ], limit=1)

            if not current_sale_order:
                continue

            # Get all previous invoices for the same sales order
            previous_invoices = self.env['account.move'].search([
                ('invoice_origin', '=', current_sale_order.name),
                ('id', '!=', line.move_id.id),
                ('state', '!=', 'cancel'),
                ('move_type', 'in', ['out_invoice', 'out_refund'])
            ])

            # Calculate total previous quantity for this product from ALL previous invoices
            prev_qty = 0.0
            for inv in previous_invoices:
                for prev_line in inv.invoice_line_ids:
                    if prev_line.product_id and prev_line.product_id.id == line.product_id.id:
                        prev_qty += prev_line.quantity

            # Set previous quantity as sum of all previous invoice quantities
            line.previous_quantity = prev_qty

            # Calculate cumulative quantity
            line.cumulative_quantity = prev_qty + line.quantity

            # Check delivered quantity
            delivered_qty = self._get_delivered_quantity(current_sale_order, line.product_id)
            if delivered_qty > 0 and line.cumulative_quantity > delivered_qty:
                line.cumulative_quantity = delivered_qty

            # Calculate cumulative price
            line.cumulative_price = line.price_unit * line.cumulative_quantity
            # Apply discount if any
            if line.discount:
                line.cumulative_price = line.cumulative_price * (1 - (line.discount / 100.0))

    def _get_delivered_quantity(self, sale_order, product):
        """
        Get the delivered quantity for a product in a sale order
        by checking the associated stock moves
        """
        delivered_qty = 0.0

        # Get all delivery orders (stock pickings) related to this sale order
        pickings = sale_order.picking_ids.filtered(lambda p: p.state != 'cancel')

        for picking in pickings:
            # Get move lines for this product that are done
            move_lines = picking.move_ids_without_package.filtered(
                lambda m: m.product_id.id == product.id and m.state == 'done'
            )
            for move in move_lines:
                # Add to delivered quantity
                delivered_qty += move.product_uom_qty

        return delivered_qty

    def handle_previous_products(self, move_id):
        """Instead of creating virtual lines, this function will compute the previous products
        and make them available for reporting without actually creating invoice lines"""
        if not move_id or not move_id.invoice_origin or move_id.move_type not in ('out_invoice', 'out_refund'):
            return []

        # Find the sale order
        sale_order = self.env['sale.order'].search([
            ('name', '=', move_id.invoice_origin)
        ], limit=1)

        if not sale_order:
            return []

        # Get all products in the current invoice
        current_invoice_products = move_id.invoice_line_ids.mapped('product_id.id')

        # Get previous invoices for this sale order, but ordered by create_date
        previous_invoices = self.env['account.move'].search([
            ('invoice_origin', '=', sale_order.name),
            ('id', '!=', move_id.id),
            ('state', '!=', 'cancel'),
            ('move_type', 'in', ['out_invoice', 'out_refund']),
            ('create_date', '<', move_id.create_date)  # Only invoices created earlier
        ], order='create_date asc')  # Order by create date ascending

        if not previous_invoices:
            return []

        virtual_lines = []

        # Get all unique products from previous invoices
        all_previous_product_ids = set()
        for inv in previous_invoices:
            for line in inv.invoice_line_ids:
                if line.product_id and line.product_id.id not in current_invoice_products:
                    all_previous_product_ids.add(line.product_id.id)

        # For each product, calculate cumulative quantities from previous invoices
        for product_id in all_previous_product_ids:
            product = self.env['product.product'].browse(product_id)

            # Get the most recent invoice line for product details
            recent_line = False
            for inv in reversed(previous_invoices):  # Reversed to get most recent first
                line = inv.invoice_line_ids.filtered(lambda l: l.product_id.id == product_id)
                if line:
                    recent_line = line[0]
                    break

            if not recent_line:
                continue

            # Find the SO line for this product
            so_line = sale_order.order_line.filtered(lambda l: l.product_id.id == product_id)
            if not so_line:
                continue

            # Calculate the total quantity from previous invoices for this product
            total_previous_qty = 0.0
            for inv in previous_invoices:
                for line in inv.invoice_line_ids:
                    if line.product_id and line.product_id.id == product_id:
                        total_previous_qty += line.quantity

            # Create a virtual line dictionary
            virtual_line = {
                'product_id': product_id,
                'product': product,
                'name': product.name,
                'description': recent_line.name,
                'previous_quantity': total_previous_qty,
                'quantity': 0.0,
                'cumulative_quantity': total_previous_qty,
                'price_unit': recent_line.price_unit,
                'discount': recent_line.discount,
                'taxes': so_line.tax_id,
                'cumulative_price': recent_line.price_unit * total_previous_qty * (
                    1 - (recent_line.discount / 100.0) if recent_line.discount else 1.0),
                'currency_id': move_id.currency_id
            }

            virtual_lines.append(virtual_line)

        return virtual_lines