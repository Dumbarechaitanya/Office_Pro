MENUS = [
    {
        'name': 'Settings',
        'sequence': 10,
        'url_path': '/settings/',
        'children': [
            {'name': 'General Settings', 'sequence': 10, 'url_path': '/settings/general/'},
            {
                'name': 'Users & Companies',
                'sequence': 20,
                'children': [
                    {'name': 'Users', 'sequence': 10, 'url_path': '/settings/users/'},
                    {'name': 'Companies', 'sequence': 20, 'url_path': '/settings/companies/'},
                    {'name': 'Privileges', 'sequence': 30, 'url_path': '/settings/privileges/'},
                ],
            },
            {
                'name': 'Technical',
                'sequence': 30,
                'children': [
                    {'name': 'Menu Items', 'sequence': 10, 'url_path': '/settings/technical/menu-items/'},
                    {'name': 'Models', 'sequence': 20, 'url_path': '/settings/technical/models/'},
                    {'name': 'Views', 'sequence': 30, 'url_path': '/settings/technical/views/'},
                    {'name': 'Sequences', 'sequence': 40, 'url_path': '/settings/technical/sequences/'},
                    {'name': 'Actions', 'sequence': 50, 'url_path': '/settings/technical/actions/'},
                    {'name': 'Fields', 'sequence': 60, 'url_path': '/settings/technical/fields/'},
                    {'name': 'Many2Many Relations', 'sequence': 70, 'url_path': '/settings/technical/m2m/'},
                    {'name': 'Cron Jobs', 'sequence': 80, 'url_path': '/settings/technical/cron/'},
                    {'name': 'Record Rules', 'sequence': 90, 'url_path': '/settings/technical/record-rules/'},
                    {'name': 'Access Rights', 'sequence': 100, 'url_path': '/settings/technical/access-rights/'},
                    {'name': 'Paper Formats', 'sequence': 110, 'url_path': '/settings/technical/paper-formats/'},
                    {'name': 'Reports', 'sequence': 120, 'url_path': '/settings/technical/reports/'},
                    {'name': 'Outgoing Mail Servers', 'sequence': 130, 'url_path': '/settings/technical/outgoing-mail/'},
                    {'name': 'Parameters', 'sequence': 140, 'url_path': '/settings/technical/parameters/'},
                ],
            },
        ],
    },
]