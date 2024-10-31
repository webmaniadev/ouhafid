odoo.define('pos_restrict_product_stock.ProductScreen', function(require) {
    "use strict";
    console.log("MOhammed Rahmoun !!!!!!!!!!!!!!!!!!!!!!");
    const Registries = require('point_of_sale.Registries');
    const ProductScreen = require('point_of_sale.ProductScreen');
    const models = require('point_of_sale.models');

    // Load the required fields

    models.load_fields('product.product', ['qty_available', 'virtual_available']);

    const RestrictProductScreen = (ProductScreen) => class extends ProductScreen {
        async _clickProduct(event) {
            const product = event.detail;
            const type = this.env.pos.config.stock_type;
            try {
                if (
                    this.env.pos.config.is_restrict_product &&
                    (
                        (type === 'qty_on_hand' && product.qty_available <= 0) ||
                        (type === 'virtual_qty' && product.virtual_available <= 0) ||
                        (type === 'both' && product.qty_available <= 0 && product.virtual_available <= 0)
                    )
                ) {
                    await this.showPopup('RestrictStockPopup', {
                        title: 'Out of Stock',
                        body: product.display_name,
                        pro_id: product.id
                    });
                    return;
                }
                await super._clickProduct(event);
            } catch (error) {
                console.error('Error in _clickProduct:', error);
                await this.showPopup('ErrorPopup', {
                    title: 'Error',
                    body: 'An error occurred while processing the product.',
                });
            }
        }
    };

    Registries.Component.extend(ProductScreen, RestrictProductScreen);

    return RestrictProductScreen;
});