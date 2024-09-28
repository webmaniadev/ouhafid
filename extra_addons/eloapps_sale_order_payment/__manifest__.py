# -*- coding: utf-8 -*-
{
    'name': "Bon de Livraison Valorisé",
    'summary': """Valued sale order and delivery slip """,


    'version': "14.0.3.1",
    'category': 'Sales/sales',

    
    "contributors": [
        "1 <Nassim REFES>",
        "2 <Ould Miloud Mohamed>",
        "3 <Chenafa Yassamine>",
        "4 <Youcef BENCHEHIDA>",
        "5 <Fatima MESSADI>",
    ],

    'company'     : 'Elosys',
    'author'      : 'Elosys',
    'maintainer'  : 'Elosys',

    'website': "https://www.elosys.net/",
    'support' : "support@elosys.net",
    #'live_test_url' : "https://www.elosys.net/shop/employes-algerie-50?category=13#attr=102",


    'sequence': 1,


   
    'depends': ['sale_management','stock','sale_stock'],


    'data': [
        'security/ir.model.access.csv',

        'reports/action_stock_picking_report.xml',
        'reports/stock_picking.xml',
        'reports/sale_report.xml',

        'wizard/sale_order_payment.xml',

        'views/account_journal.xml',
        'views/account_payment.xml',
        'views/sale_order.xml',
        'views/account_move_line.xml',
        'views/stock_picking.xml',
        'views/add_print_button.xml',

        'wizard/sale_payment.xml',
    ],


    'license': "LGPL-3",
    'price': "109.99",
    'currency': 'Eur',


    'images'        : [
        'images/banner.gif'
        ],



    'installable': True,
    'auto_install': False,
}
