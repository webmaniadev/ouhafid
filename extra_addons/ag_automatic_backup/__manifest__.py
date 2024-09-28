# -*- coding: utf-8 -*-
{
    'name': 'Automatic Backup Odoo',
    'version': '14.0',
    'summary': 'Automatic Backup',
    'author': 'APPSGATE FZC LLC',
    'description': """
    Automatic Backup,
    Backup
    """,
    'data': [
        'data/data.xml',
        'views/automatic_backup.xml',
        'security/security.xml'
    ],
    'depends': [
        'mail',
    ],
    'images': [
        'static/src/img/main-screenshot.png'
    ],
    'installable': True,
    'application': True,
    'price': 20.00,
    'currency': 'USD',
}
