# -*- coding: utf-8 -*-
{
    'name': "Modify sequence",

    'summary': """
    modifier les factures 
        """,
    'description': """
    modifier les factures 
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list

    'category': 'Sale',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale_management', 'stock', 'sale_stock', 'eloapps_sale_order_payment','account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/res_config.xml',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
