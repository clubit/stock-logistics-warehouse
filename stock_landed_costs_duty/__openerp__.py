{
    'name': 'Landed Costs Duty',
    'summary': 'Add the possibility for duty calculation',
    'version': '1.0',
    'category': 'Warehouse Management',
    'author': 'Clubit BVBA',
    'website': 'http://www.clubit.be',
    'depends': [
        'product',
        'stock_landed_costs',
        ],
    'data': [
        'data/product_data.xml',
        'views/product_view.xml',
        'views/stock_landed_costs_view.xml',
    ],
    'installable': True,
    'auto_install': False,
}