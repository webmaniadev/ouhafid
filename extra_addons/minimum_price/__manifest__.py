# -*- coding: utf-8 -*-
{
    'name': "Webmania Minimum Price Module",
    'summary': """
Lock and control your minimum sale price to POS, Sales Order and Invoice
""",
    'description': """
        Lock and control your minimum sale price to POS, Sales Order and Invoice
    """,

    'author': "webmania",
    'website': "https://www.webmania.ma/",
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Sale',
    'version': '0.1',
    # any module necessary for this one to work correctly
    'depends': ['base', 'sale'],
    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/point_of_sale.xml',
        'views/product_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
