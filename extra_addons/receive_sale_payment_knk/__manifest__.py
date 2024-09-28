# -*- coding: utf-8 -*-
# Powered by Kanak Infosystems LLP.
# © 2020 Kanak Infosystems LLP. (<https://www.kanakinfosystems.com>)
{
    'name': 'Receive Sale Payment',
    'version': '1.0',
    'summary': 'Using this module user can receive directly payment from sale order. | sale order  | Advance payment | sale payment',
    'description': """Using this module user can receive directly payment from sale order.
    """,
    'category': 'Sales/Sales',
    'license': 'OPL-1',
    'author': 'Kanak Infosystems LLP.',
    'website': 'https://www.kanakinfosystems.com',
    'depends': ['sale_management', 'account'],
    'images': ['static/description/banner.png'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'wizard/receive_sale_payment.xml',
        'views/sale_order_view.xml',
        'report/sale_report_templates.xml',
        'views/account_payment_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'price': 10,
    'currency': 'EUR',
}
