# -*- coding: utf-8 -*-
{
    'name': "Bl Quantity",
    'summary': """
        Add total quantities to Bl report""",
    'description': """
        This module adds total quantities to facture report:
        * Shows total number of products
        * Displays sum of all quantities
        * Adds totals at bottom of delivery slip
    """,
    'author': "webmania",
    'website': "http://www.webmania.ma",
    'category': 'Inventory',
    'version': '14.0.1.0.0',
    'depends': ['base', 'stock', 'account'],
    'data': [
        'report/bl_qte_total.xml',
    ],
}
