
{
    'name': 'Sale Order Quotation Control',
    'version': '14.0.1.0.0',
    'category': 'Sales',
    'summary': 'Control quotation creation based on user groups',
    'description': """
        This module restricts the visibility of the 'Create Quotation' action in the sale order based on user groups.
    """,
    'author': 'Webmania',
    'depends': ['sale'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/sale_order_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
