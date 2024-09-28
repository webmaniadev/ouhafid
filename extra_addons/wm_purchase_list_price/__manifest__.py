# -*- coding: utf-8 -*-


{
    'name': 'Modifier le prix de l''article pendant le processus d''achat.',
    'summary': """Des ajustements de prix en temps réel assurent des coûts précis lors de l'achat.""",
    'version': '14.0.1.0.0',
    'description': """L'implémentation de mécanismes de tarification dynamique permet des modifications instantanées des prix tout au long du parcours d'achat, assurant des tarifs précis et actuels au moment de la transaction.""",
    'author': 'webmania',
    'company': 'Cwebmania',
    'website': 'https://www.webmania.ma',
    'category': 'Extra Tools',
    'depends': ['base', 'purchase'],
    'data': [
          'views/purchase_order_line_inherit.xml'
    ],
    'installable': True,
    'auto_install': False,

}
