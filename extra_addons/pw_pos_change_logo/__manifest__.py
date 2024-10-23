# -*- coding: utf-8 -*-
{
    "name": "POS Change Logo on POS Screen and Receipt | Change POS Logo",
    "version": "13.0",
    'summary': """
        This module is allow to set Logo on Screen and POS Receipt | Logo on POS Receipt and Screen | Change POS logo""",
    'description': """
        This module is allow to set Logo and Barocode on pos receipt
- POS Logo on Receipt
- Logo on pos Screen
        """,    
    "category": "Point Of Sale",
    'author': "Preway IT Solutions",
    "sequence": 2,
    "summary": "",
    "depends" : ["point_of_sale"],
    "data" : [
        "views/assets.xml",
        "views/pos_config_view.xml",
    ],
    'qweb': ['static/src/xml/pos.xml'],
    'price': 7.0,
    'currency': 'EUR',
    "installable": True,
    "auto_install": False,
    "images":["static/description/Banner.png"],
}
