odoo.define('pw_pos_change_logo.pw_pos_change_logo', function (require) {
"use strict";

var screens = require('point_of_sale.screens');
var rpc = require('web.rpc');
var core = require('web.core');
var models = require('point_of_sale.models');
var QWeb = core.qweb;
var chrome = require('point_of_sale.chrome');
models.load_fields('pos.config', ['pw_change_logo', 'pw_pos_logo']);

chrome.Chrome.include({
    build_chrome: function() { 
        var self = this;
        this._super();
        if (this.pos.config.pw_change_logo) {
            var url = window.location.origin + '/web/image?model=pos.config&field=pw_pos_logo&id='+self.pos.config.id;
            $('.pos-logo').attr("src", url);
        }
    },
});
var _super_Order = models.Order.prototype;
models.Order = models.Order.extend({
    export_for_printing: function () {
        var res = _super_Order.export_for_printing.apply(this, arguments);
        res['pw_pos_logo'] = 'data:image/png;base64,'+this.pos.config.pw_pos_logo;
        return res;
    },
});
});