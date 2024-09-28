# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    "name" : "Add Cheque Details on Payment",
    "version" : "14.0.0.0",
    "category" : "Accounting",
    'summary': "Add cheque number on payment add cheque image on payment Add cheque number on Account payment add cheque image on Account payment manual check number on payment manual check details on payment account payment check details check number on payment check",
    "description": """
    
        This odoo app helps user to add cheque number and image on payment, User can add both cheque number and image while registering payment for invoice and also can add for validated payment, Added check number can printed on payment report.
    
    """,
    "author": "BrowseInfo",
    "website" : "https://www.browseinfo.in",
    "price": 10,
    "currency": 'EUR',
    "depends" : ["account"],
    "data": [
        "views/payment_receipt_document_inherit_report.xml",
        "views/account_payment_inherit_views.xml",  
        "wizard/account_payment_register_inherit_wizard_views.xml",
    ],
    "qweb" : [],
    "auto_install": False,
    "installable": True,
    "live_test_url":"https://youtu.be/6x_qaXc485Q",
    "images":["static/description/Banner.png"],
}
