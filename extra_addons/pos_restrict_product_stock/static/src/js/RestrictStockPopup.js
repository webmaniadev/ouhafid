odoo.define('pos_restrict_product_stock.RestrictStockPopup', function(require) {
    "use strict";

    const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
    const Registries = require('point_of_sale.Registries');

    class RestrictStockPopup extends AbstractAwaitablePopup {
        setup() {
            super.setup();
        }

        async orderProduct() {
            var product = this.env.pos.db.get_product_by_id(this.props.pro_id);
            if (product) {
                this.env.pos.get_order().add_product(product);
            }
            this.confirm();
        }
    }

    RestrictStockPopup.template = 'RestrictStockPopup';
    Registries.Component.add(RestrictStockPopup);

    return RestrictStockPopup;
});