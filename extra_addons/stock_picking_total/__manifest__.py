# -*- coding: utf-8 -*-
{
    'name': "Stock Picking Total Quantity",
    'summary': """
        Add total quantities to delivery slip report""",
    'description': """
        This module adds total quantities to delivery slip report:
        * Shows total number of products
        * Displays sum of all quantities
        * Adds totals at bottom of delivery slip
    """,
    'author': "webmania",
    'website': "http://www.webmania.ma",
    'category': 'Inventory',
    'version': '14.0.1.0.0',
    'depends': ['base', 'stock'],
    'data': [
        'report/report_delivery_total_quantity.xml',
        'report/report_delivery_total_qte_package.xml',
    ],
}
