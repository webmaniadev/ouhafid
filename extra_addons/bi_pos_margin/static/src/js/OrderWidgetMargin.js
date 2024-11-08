odoo.define('bi_pos_margin.OrderSummaryMargin', function(require){
	'use strict';

	const OrderSummary = require('point_of_sale.OrderSummary');
	const PosComponent = require('point_of_sale.PosComponent');
	const Registries = require('point_of_sale.Registries');
	const { Component } = owl;

	const OrderSummaryMargin = (OrderSummary) =>
		class extends OrderSummary {
			constructor() {
				super(...arguments);
			}

			get total_margin(){
				let order = this.env.pos.get_order();			       		        
		        let margin = order ? order.get_total_margin() : 0;
		        return margin.toFixed(2);
			}

		};

	Registries.Component.extend(OrderSummary, OrderSummaryMargin);

	return OrderSummary;

});