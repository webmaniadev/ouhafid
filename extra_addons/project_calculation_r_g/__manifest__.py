# -*- coding: utf-8 -*-
{
    'name': "Project RG calculation",
    'description': """
       This module calclul RG .
    """,
    'author': "WEBMANIA",
    'website': "http://www.webmania.ma",
    'category': 'Project',
    'version': '14',
    'depends': ['base' , 'project', 'account' , 'sale', 'project_cution', 'stock'],
    'data': [
        'report/inherit_report_account_move.xml',
        'report/report_bordereau_realise.xml',
        'views/view_config.xml',
        'views/view_project.xml',
        'views/view_account_move.xml',
        'views/view_sale_order.xml',
        'views/view_stock_picking.xml',
    ],
}










