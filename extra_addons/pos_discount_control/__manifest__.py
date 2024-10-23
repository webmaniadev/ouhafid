# -*- coding: utf-8 -*-
{
    'name': 'POS Discount Control',
    'version': '14.0.1',
    'category': 'Point of Sale',
    "license": "OPL-1",
    'price': 9,
    'currency': 'EUR',
    'description': """
        Restrict discount modification to managers
    """,
    'author': 'Felix VNM',
    'depends': [
        'point_of_sale',
        'pos_hr'
    ],
    'data': [
        "views/pos_config_view.xml",
        "views/pos_view.xml",
    ],

    'test': [],
    'demo': [],
    'qweb': [

    ],
    'images': ['static/description/banner.png'],
    'installable': True,
    'active': True,
    'application': False,
}
