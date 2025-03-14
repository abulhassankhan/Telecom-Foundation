{
    'name': "AH Custom Employee",


    'author': "Abul Hassan Khan Ghauri",
    'website': "https://abulhassan.kesug.com",
    'support': "ahassankg@gmail.com",

    'category': 'Abul Hassan',
    'version': '0.1',

    'depends':['base', 'hr', 'hr_contract', 'sm_custom_project_apps', 'c2p_payroll_customization'],

    'data': [
        'views/hr_employee.xml',
        'views/hr_contract.xml',
        'views/hr_payroll_structure.xml',
        # 'views/default_project_users.xml',
        # 'views/pms_report_view.xml',
        #
        # 'security/ir.model.access.csv'
    ],
}
