# -*- coding: utf-8 -*-
{
    'name': "Project Status Control",
    'summary': """
        Control project status progression""",
    'description': """
        This module adds status sequence control to projects:
        - Prevents moving projects to previous statuses
        - Adds special group for status bypass
        - Enforces one-way project progression
    """,
    'author': "WEBMANIA",
    'website': "http://www.webmania.ma",
    'category': 'Project',
    'version': '14.0.1.0.0',
    'depends': ['base', 'project' , 'project_status'],
    'data': [
          'security/group_project_controle.xml',
    ],
}
