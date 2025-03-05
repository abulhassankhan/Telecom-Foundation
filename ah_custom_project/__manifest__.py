{
    'name': "AH Custom Project",


    'author': "Abul Hassan Khan Ghauri",
    'website': "https://abulhassan.kesug.com",
    'support': "ahassankg@gmail.com",

    'category': 'Uncategorized',
    'version': '0.1',

    'depends':['project', 'sm_custom_project_apps'],

    'data': [
        'views/project_task.xml',
        'views/project_project.xml',
        'views/default_project_users.xml',
        'views/pms_report_view.xml',
        'views/project_task_executive_appraisal_view.xml',

        'security/ir.model.access.csv'
    ],

}
