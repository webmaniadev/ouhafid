# -*- coding: utf-8 -*-
{
    'name': 'Product Name With Non-Reserved Qty',
    'version': '14.0.1.0.0',
    'category': 'Sales',
    'summary': 'Display product name with non-reserved quantity in sale order lines',
    'author': 'WEBMANIA SOLUTION',
    'website': 'https://www.webmania.ma',
    'depends': [
        'product',
        'sale',
        'sale_stock',
        'stock_available_unreserved',  # Dependency on your existing module
    ],
    'data': [
        'views/sale_order_views.xml',
        'views/stock_picking_view.xml',
        'views/assets.xml',

    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
