# -*- coding: utf-8 -*-
{

    'name': "Sale Margin Calcule",
    'description': """
        This gives the profitability by calculating the difference between the Unit
    Price and Cost Price
    """,
    'author': "Webmania",
    'website': "https://www.webmania.ma",
    'category': 'Sales Management',
    'version': '0.1',
    'depends': ['base', 'sale_margin' , 'product'],
    'data': [
        # 'security/ir.model.access.csv',
        'views/hook_view_product_price_list.xml',
        'views/sale_margin_view.xml',
        'views/view_sale_order.xml',
    ],
}
