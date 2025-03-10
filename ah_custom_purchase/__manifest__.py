{
    'name': "AH Custom Purchase",


    'author': "Abul Hassan Khan Ghauri",
    'website': "https://abulhassan.kesug.com",
    'support': "ahassankg@gmail.com",

    'category': 'Abul Hassan',
    'version': '0.1',

    'depends':['purchase', 'base', 'purchase_requisition', 'sh_all_in_one_helpdesk'],

    'data': [
        'views/purchase_order.xml',

        'data/sequences.xml',

        # 'security/ir.model.access.csv'
    ],
}
