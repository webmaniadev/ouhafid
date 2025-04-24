# -*- coding: utf-8 -*-
{
    'name': "Project Invoice Link",

    'description': """
        Project Invoice Link
    """,

    'author': "webmania",
    'website': "http://www.webmania.ma",

    'category': 'Project',
    'version': '0.1',

    'depends': ['base', 'sale', 'project'],
    'data': [
        # 'security/ir.model.access.csv',
        'views/project_sale_invocie_view.xml',
    ],
}
