odoo.define('bi_pos_margin.point_of_sale', function (require) {
    "use strict";

    var models = require('point_of_sale.models');
    var utils = require('web.utils');

    models.load_fields('res.users', ['print_margin_show']);
});