# -*- coding: utf-8 -*-
{
    'name': 'Contracting Type',
    'version': '14.0.1',
    'description': '',
    'summary': '',
    'author': "Ahmad Hasan - Flex-Ops",
    'website': "https://flex-ops.com",
    'depends': ['base', 'sale'],

    'data': [
        'security/ir.model.access.csv',
        'views/contract_hotel_view.xml',
        'views/contract_transportation_view.xml',
        'views/contract_restaurant_view.xml',
        'views/contract_guide_view.xml',
        'views/menu.xml',
        'views/hotel_season_view.xml',
        'views/hotel_promotion_view.xml',

    ],

    'installable': True,
    'auto_install': False,
}
