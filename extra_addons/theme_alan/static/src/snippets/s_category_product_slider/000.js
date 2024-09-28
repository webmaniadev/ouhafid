odoo.define('theme_alan.s_category_product_slider',function(require){
'use strict';

var sAnimation = require('website.content.snippets.animation');
var ajax = require('web.ajax');

sAnimation.registry.category_product_slider_actions = sAnimation.Class.extend({
    selector : '.as_category_product',
    disabledInEditableMode: false,
    start: function (editable_mode) {
        var self = this;
        if (self.editableMode){
            var getSliderName = self.$target.attr('data-slider-style-name') == undefined ? '' : self.$target.attr('data-slider-style-name') ;
            self.$target.find('div').empty().append('<div class="seaction-head"><h2>Category Product Slider: '+ getSliderName  +'</h2></div>');
        }
        if(!self.editableMode){
            var style_id = self.$target.attr('data-slider-style-id');
            var category_ids = self.$target.attr('data-slider-category-id');
            ajax.jsonRpc('/get_category_products_data', 'call',
                {'style_id': style_id,'category_ids':category_ids})
            .then(function (data) {
                if(data){
                    self.$target.find('div').empty().append(data);
                    self.initialize_owl();
                }
            });
        }
    },
    initialize_owl: function () {
        $('.as-product-carousel').owlCarousel({
            loop: false,
            rewind: true,
            margin: 10,
            nav: true,
            lazyLoad:true,
            dots: false,
            navText : ['<span aria-label="Previous"></span>', '<span aria-label="Next"></span>'],
            items: 4,
            responsive: {
                0: {
                    items: 1,
                },
                481: {
                    items: 2,
                },
                768: {
                    items: 2,
                },
                1024: {
                    items: 4,
                },
                1200: {
                    items: 4,
                }
            },
        });
    },
});
});