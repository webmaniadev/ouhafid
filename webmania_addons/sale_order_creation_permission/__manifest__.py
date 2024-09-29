
{
    'name': 'Sale Order Creation Permission',
    'version': '14.0.2.0',
    'category': 'Sales',
    'summary': 'Control sale order creation visibility for users.',
    'depends': ['base', 'sale'],
    'data': [
        'views/res_users_view.xml',
        'views/sale_order_view.xml',
    ],
    'installable': True,
    'application': False,
}
