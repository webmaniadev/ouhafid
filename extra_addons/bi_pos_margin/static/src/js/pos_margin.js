odoo.define('bi_pos_margin.pos', function(require){
	'use strict';

	var models = require('point_of_sale.models');
	var core = require('web.core');
	var QWeb = core.qweb;
	const { Component } = owl;


    var _super_posmodel = models.PosModel.prototype;
    models.PosModel = models.PosModel.extend({
        initialize: function(session, attributes) {
            var product_model = _.find(this.models, function(model){ return model.model === 'product.product'; });
            product_model.fields.push('standard_price');
            //console.log("partner loadedddddddddddddddddddddddddddddddddddd",product_model);

            return _super_posmodel.initialize.call(this, session, attributes);
        },

    });


	var OrderlineSuper = models.Orderline;
    models.Orderline = models.Orderline.extend({
		initialize: function(attr,options){
		OrderlineSuper.prototype.initialize.apply(this, arguments);
        this.pos   = options.pos;
        this.order = options.order;
        
        if (options.json) {
            this.init_from_JSON(options.json);
            return;
        }

        this.set_staystr();
        this.set_orderline_margin();
        //console.log('o****************************************************88line', this)

    },
    clone: function(){
        var orderline = new exports.Orderline({},{
            pos: this.pos,
            order: null,
            product: this.product,
            price: this.price,
        });
        
        orderline.quantity = this.quantity;
        orderline.quantityStr = this.quantityStr;
        orderline.stayStr = this.stayStr;
        orderline.discount = this.discount;
        orderline.type = this.type;
        orderline.selected = false;
        orderline.margin = this.margin;
        //console.log('o****************************************************88line', orderline, this)
        return orderline;
    },
    
    set_staystr: function(){
    
	  return this.margin;
    },

    set_orderline_margin: function(){
    	var product_price = this.price;
    	var cost = this.product.standard_price;
    	var product_qty = this.quantity;
    	var margin = (product_price - cost)* product_qty;
    	console.log(this,"------margin")
    	this.margin = margin
    	console.log(margin,"-----margin")
    	return margin

    },
    
    
    });

        // exports.Orderline = Backbone.Model.extend ...
   var OrderSuper = models.Order;
    models.Order = models.Order.extend({
	    get_total_margin:function() {
           var utils = require('web.utils');
           var round_pr = utils.round_precision;
            return round_pr(this.orderlines.reduce((function(sum, orderLine) {
            return sum + orderLine.margin;

        }), 0), this.pos.currency.rounding);
    sum
        },
    
    });
	
});

