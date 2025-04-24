odoo.define('product_name_with_nonreserved_qty.product_selection', function (require) {
    "use strict";

    var core = require('web.core');
    var FieldMany2One = require('web.relational_fields').FieldMany2One;
    var fieldRegistry = require('web.field_registry');

    // Define the sale label
    var SALE_LABEL = "VENTE";

    var ProductSelectionWidget = FieldMany2One.extend({
        /**
         * Override the _renderEdit method to add a new event listener for when
         * the autocomplete dropdown is opened
         */
        _renderEdit: function () {
            this._super.apply(this, arguments);
            var self = this;

            // When the autocomplete dropdown opens
            this.$input.on('autocompleteopen', function () {
                // Use setTimeout to let the DOM render first
                setTimeout(function () {
                    // Find all dropdown items
                    $('.ui-autocomplete .ui-menu-item').each(function () {
                        var $item = $(this);
                        var text = $item.text();

                        // Look for our format pattern "- VENTE: X"
                        var regex = new RegExp('- ' + SALE_LABEL + ': (\\d+)');
                        var match = text.match(regex);

                        if (match) {
                            var qty = parseInt(match[1]);
                            var $itemContent = $item.find('a');

                            // Determine color based on quantity
                            var color = qty <= 0 ? 'red' : 'green';

                            // Color both the VENTE label and quantity
                            var newText = text.replace(
                                new RegExp('(- )(' + SALE_LABEL + ')(: )(\\d+)'),
                                function(match, prefix, label, colon, number) {
                                    return prefix +
                                           '<span style="color:' + color + ';">' +
                                           label +
                                           '</span>' +
                                           colon +
                                           '<span style="color:' + color + ';">' +
                                           number +
                                           '</span>';
                                }
                            );

                            // Apply the formatted content
                            $itemContent.html(newText);
                        }
                    });
                }, 0);
            });
        }
    });

    // Register our custom widget
    fieldRegistry.add('product_selection_colored', ProductSelectionWidget);

    return {
        ProductSelectionWidget: ProductSelectionWidget
    };
});