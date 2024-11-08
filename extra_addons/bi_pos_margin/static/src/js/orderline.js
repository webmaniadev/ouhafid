odoo.define('bi_pos_margin.OrderLine', function(require){
	'use strict';

	const Orderline = require('point_of_sale.Orderline');
	const PosComponent = require('point_of_sale.PosComponent');
	const Registries = require('point_of_sale.Registries');
	const { Component } = owl;

	const OrderMargin = (Orderline) =>
		class extends Orderline {
			constructor() {
				super(...arguments);
				// console.log("-------OrderWidgetMargin")
			}

			get set_margin(){
					console.log(this,"------setmargin")
					var product_price = this.price;
			    	var cost = this.product.standard_price;
			    	var product_qty = this.quantity;
			    	var margin = (product_price - cost)* product_qty;
			    	this.margin = margin
			    	console.log(margin,"-----setmargin")
			    	return margin
				}

  	};

    Registries.Component.extend(Orderline, OrderMargin);

    return OrderReceipt;
});