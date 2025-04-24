# -*- coding: utf-8 -*-
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

{
    'name': 'Kitmed stock reports BS, BR',
    'version': '14.0.1.0.0',
    'category': 'Generic Modules/Others',
    'description': 'ADD Bon de sortie & Bon de retour',
    'summary': 'ADD Bon de sortie & Bon de retour',
    'author': 'Webmania',
    'maintainer': 'webmania',
    'website': 'http://webmania.ma',
    'support': 'odoomates@gmail.com',
    'license': 'LGPL-3',
    'depends': [
       'stock'
    ],
    'data': [
        'report/report_bon_sortie.xml',
        'report/report_bon_retour.xml',
        'report/kitmed_report_view.xml',

    ],

    'demo': [],
    'test': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
