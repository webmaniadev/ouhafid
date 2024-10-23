odoo.define('pos_discount_control.NumpadWidget', function(require) {
    'use strict';

    const NumpadWidget = require('point_of_sale.NumpadWidget');
    const Registries = require('point_of_sale.Registries');

    const DiscountControlNumpad = NumpadWidget => class extends NumpadWidget {

        get hasManualDiscount() {
            var has_disc_rights = super.hasPriceControlRights;
            if (!!has_disc_rights) {
                var cashier = this.env.pos.get('cashier') || this.pos.get_cashier();
                has_disc_rights = !this.env.pos.config.restrict_discount_control || cashier.role == 'manager';
            }
            return has_disc_rights;
        }
    };
    Registries.Component.extend(NumpadWidget, DiscountControlNumpad);
    return NumpadWidget;
 });
