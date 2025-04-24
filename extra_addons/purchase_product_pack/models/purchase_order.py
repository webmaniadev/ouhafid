# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import _, api, models
from odoo.exceptions import UserError


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def copy_data(self, default=None):
        data_list = super(PurchaseOrder, self).copy_data(default=default)
        for data in data_list:
            order_lines = data["order_line"]
            new_order_lines = []  # Create a new list for modified order_lines
            for order_line in order_lines:
                # In Odoo 14, the structure might be different, verify the list access
                if len(order_line) >= 3 and isinstance(order_line[2], dict):
                    pack_parent_id = order_line[2].get("pack_parent_line_id", False)
                    if pack_parent_id:
                        pack_parent = self.env["purchase.order.line"].browse(pack_parent_id)
                        if not (pack_parent and pack_parent.order_id == self):
                            # Add non-excluded lines to new_order_lines
                            new_order_lines.append(order_line)
                    else:
                        new_order_lines.append(order_line)
                else:
                    new_order_lines.append(order_line)
            # Update 'order_line' in the data dictionary
            data["order_line"] = new_order_lines
        return data_list

    @api.onchange("order_line")
    def check_pack_line_unlink(self):
        # At least on embeded tree editable view odoo returns a recordset on
        # origin.order_line only when lines are unlinked and this is exactly
        # what we need
        origin_line_ids = self._origin.order_line.ids
        line_ids = self.order_line.ids
        removed_line_ids = set(origin_line_ids) - set(line_ids)
        removed_line = self.env["purchase.order.line"].browse(removed_line_ids)
        if removed_line.filtered(
            lambda x: x.pack_parent_line_id
            and not x.pack_parent_line_id.product_id.pack_modifiable
        ):
            raise UserError(
                _(
                    "You cannot delete this line because is part of a pack in"
                    " this purchase order. In order to delete this line you need to"
                    " delete the pack itself"
                )
            )

    def write(self, vals):
        if "order_line" in vals:
            self._check_deleted_line(vals)
        return super(PurchaseOrder, self).write(vals)

    def _check_deleted_line(self, vals):
        """
        When updating a purchase order, this method checks for deleted lines in
        the 'order_line' field. If any purchase order lines are marked for deletion,
        it also identifies and remove any subpack lines that are associated with
        these deleted lines but not marked for deletion.
        """
        to_delete_ids = [e[1] for e in vals["order_line"] if e[0] == 2]
        if to_delete_ids:
            # In Odoo 14, child_of operator might work differently in some edge cases
            # Let's use a more explicit domain for better compatibility
            subpacks = self.env["purchase.order.line"].search([
                ("pack_parent_line_id", "in", to_delete_ids),
                ("id", "not in", to_delete_ids)
            ])
            subpacks_to_delete_ids = subpacks.ids
            
            if subpacks_to_delete_ids:
                for cmd in vals["order_line"]:
                    if isinstance(cmd, list) and len(cmd) > 1:
                        if cmd[1] in subpacks_to_delete_ids:
                            if cmd[0] != 2:
                                cmd[0] = 2
                            subpacks_to_delete_ids.remove(cmd[1])
        return True