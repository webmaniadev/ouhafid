
{
    'name': 'Sale Order Creation Permission',
    'version': '14.0.1.0',
    'category': 'Sales',
    'summary': 'Control sale order creation permission for users.',
    'depends': ['base', 'sale'],
    'data': [
        'views/res_users_view.xml',
    ],
    'installable': True,
    'application': False,
}
