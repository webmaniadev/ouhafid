# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.
{
    'name': "Create Invoice On Delivery | Automatic Invoice From Delivery Order",
    'author' : 'Softhealer Technologies',
    'website': 'https://www.softhealer.com',
    "support": "support@softhealer.com",
    'category': 'Accounting',
    'version': '14.0.1',
    "license": "OPL-1",
    "summary": "Invoice From Picking,Invoice Based On Delivery Order,Invoice On Validate Delivery,Invoice On Delivery Order Validate,Invoice based on delivered Quantity,Invoice based on Ordered Quantity,Auto Invoice from Delivery Order Odoo",
    "description": """Sometimes in business, we need to create a direct invoice based on the delivery order. This module creates invoice from delivery order when validating delivery order. If you activate the "send invoice email when delivery validates" option then it auto sends invoices by email when you validate the delivery order.""",
    'depends': ['sale_management', 'stock'],
    'data': [
        'views/res_config_settings.xml',
        'views/stock_picking.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'images': ['static/description/background.png', ],
    "price": 15,
    "currency": "EUR"
}
