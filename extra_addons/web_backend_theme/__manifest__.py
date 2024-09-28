# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Web BackEnd Theme',
    'category': 'Hidden',
    'version': '1.0',
    'author': 'Mehdi HJ',
    'description':
        """
Odoo BackEnd Web Client Theme.
===========================

This module modifies the web addon to provide new theme design and responsiveness.
        """,
    'depends': ['web'],
    'auto_install': False,
    'data': [
        'views/webclient_templates.xml',
    ],
    'qweb': [
        "static/src/xml/*.xml",
    ],
}
