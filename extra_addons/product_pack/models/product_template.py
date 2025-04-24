# Copyright 2019 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    pack_type = fields.Selection(
        [("detailed", "Détaillé"), ("non_detailed", "Non détaillé")],
        "Type de pack",
        help="Dans les commandes de vente ou d'achat :\n"
             "* Détaillé : Afficher les composants individuellement dans la commande de vente.\n"
             "* Non détaillé : Ne pas afficher les composants individuellement dans la commande de vente."
    )
    pack_component_price = fields.Selection(
        [
            ("detailed", "Détaillé par composant"),
            ("totalized", "Totalisé dans le produit principal"),
            ("ignored", "ignoré"),
        ],
        "Prix du composant du pack",
        help="Dans les commandes de vente ou d'achat:\n"
        "* Détaillé par composant : Détail des lignes avec les prix.\n"
        "* Totalisé dans le produit principal : Détail des lignes en fusionnant "
        "les prix des lignes sur le pack (ne pas afficher les prix des composants).\n"
        "* Ignoré : Utiliser le prix du pack produit (ignorer les prix des lignes détaillées).",
    )
    pack_ok = fields.Boolean(
        "Est-ce un pack?",
        help="Est-ce un pack de produits ?",
    )
    pack_line_ids = fields.One2many(
        related="product_variant_ids.pack_line_ids",
    )
    used_in_pack_line_ids = fields.One2many(
        related="product_variant_ids.used_in_pack_line_ids",
        readonly=True,
    )
    pack_modifiable = fields.Boolean(
        help="Si vous cochez ce champ, vous pourrez modifier "
        "les lignes de commande de vente/achat liées à ses composants.",
    )

    @api.onchange("pack_type", "pack_component_price")
    def onchange_pack_type(self):
        products = self.filtered(
            lambda x: x.pack_modifiable
            and (x.pack_type != "detailed" or x.pack_component_price != "detailed")
        )
        for rec in products:
            rec.pack_modifiable = False

    @api.constrains("company_id", "product_variant_ids")
    def _check_pack_line_company(self):
        """Check packs are related to packs of same company."""
        for rec in self:
            for line in rec.pack_line_ids:
                if (
                    line.product_id.company_id and rec.company_id
                ) and line.product_id.company_id != rec.company_id:
                    raise ValidationError(
                        _(
                            "Les produits des lignes de pack doivent avoir la même "
                            "entreprise que celle du produit parent"
                        )
                    )
            for line in rec.used_in_pack_line_ids:
                if (
                    line.product_id.company_id and rec.company_id
                ) and line.parent_product_id.company_id != rec.company_id:
                    raise ValidationError(
                        _(
                            "Les produits des lignes de pack doivent appartenir à la même "
                            "entreprise que celle du produit parent"
                        )
                    )

    def write(self, vals):
        """We remove from product.product to avoid error."""
        _vals = vals.copy()
        if vals.get("pack_line_ids", False):
            self.product_variant_ids.write({"pack_line_ids": vals.get("pack_line_ids")})
            _vals.pop("pack_line_ids")
        return super().write(_vals)
