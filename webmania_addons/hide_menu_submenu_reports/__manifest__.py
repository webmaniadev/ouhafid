

{
    "name": "Hide Menu, Submenu, Fields and Reports",

    "version": "14.0.0.3",
    "category": "Extra Tools",
    "depends": ['base'],
    "author": "Techspawn Solutions",

    "summary": """ Hide Menu, Submenu, Fields and Reports Hide any Menu,Hide any Submenu,Hide Field on the view,Make Field readonly and Hide any Reports for any 	Users Restrictions and Groups with just one click.""",
    "description": """
        Hide any menu, sub menu, fields, report for any users and groups
    """,

    'license': "OPL-1",
    "website": "http://www.techspawn.com",

    "price": 9,
    "currency": 'USD',

    "data": [
        'security/ir.model.access.csv',
        'views/user_res.xml',
        'views/group_res.xml',
        'views/report_ir_actions.xml',
        'views/ir_model_fields_view.xml',
    ],


    "auto_install": False,
    "installable": True,
    "images": ['static/description/main.gif'],
}

