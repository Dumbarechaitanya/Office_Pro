from django.urls import path
from base import views

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard_view, name='dashboard_home'),

    # Apps Store & Modules (ir.module.module)
    path('apps/', views.apps_store, name='apps_store'),
    path('apps/modules/<str:module_name>/', views.module_detail, name='module_detail'),

    # Settings
    path('settings/', views.settings_home, name='settings_home'),
    path('settings/general/', views.settings_home, name='settings_general'),
    path('batch-action/', views.batch_action, name='batch_action'),


    # Settings > Users & Companies
    path('settings/users/new/', views.settings_user_create, name='settings_user_create'),
    path('settings/users/', views.settings_users, name='settings_users'),
    path('settings/users/<int:user_id>/', views.settings_user_detail, name='settings_user_detail'),
    path('settings/users/<int:user_id>/change-password/', views.settings_user_change_password, name='settings_user_change_password'),
    path('settings/users/<int:user_id>/create-employee/', views.settings_user_create_employee, name='settings_user_create_employee'),
    path('settings/users/<int:user_id>/send-invitation/', views.settings_user_send_invitation, name='settings_user_send_invitation'),
    path('settings/users/<int:user_id>/invitation-preview/', views.settings_user_invitation_preview, name='settings_user_invitation_preview'),
    path('settings/groups/new/', views.settings_group_create, name='settings_group_create'),
    path('settings/groups/', views.settings_groups, name='settings_groups'),
    path('settings/groups/<int:group_id>/', views.settings_group_detail, name='settings_group_detail'),
    path('settings/groups/<int:group_id>/add-user/', views.settings_group_add_user, name='settings_group_add_user'),
    path('settings/groups/<int:group_id>/remove-user/<int:user_id>/', views.settings_group_remove_user, name='settings_group_remove_user'),
    # Privileges
    path('settings/privileges/new/', views.settings_privilege_create, name='settings_privilege_create'),
    path('settings/privileges/', views.settings_privileges, name='settings_privileges'),
    path('settings/privileges/<int:privilege_id>/', views.settings_privilege_detail, name='settings_privilege_detail'),
    path('settings/privileges/<int:privilege_id>/add-group/', views.settings_privilege_add_group, name='settings_privilege_add_group'),
    path('settings/privileges/<int:privilege_id>/remove-group/<int:group_id>/', views.settings_privilege_remove_group, name='settings_privilege_remove_group'),

    # Companies
    path('settings/companies/new/', views.settings_company_create, name='settings_company_create'),
    path('settings/companies/', views.settings_companies, name='settings_companies'),
    path('settings/companies/<int:company_id>/', views.settings_company_detail, name='settings_company_detail'),

    # Contacts / Partners (res.partner)
    path('settings/contacts/new/', views.settings_partner_create, name='settings_partner_create'),
    path('settings/contacts/', views.settings_partners, name='settings_partners'),
    path('settings/contacts/<int:partner_id>/', views.settings_partner_detail, name='settings_partner_detail'),

    # Chatter / Popovers & Activities
    path('mail/post-message/', views.mail_post_message, name='mail_post_message'),
    path('mail/conversations/', views.mail_conversations, name='mail_conversations'),
    path('mail/direct-message/send/', views.mail_send_direct_message, name='mail_send_direct_message'),
    path('mail/messages/<int:msg_id>/mark-read/', views.mail_mark_message_read, name='mail_mark_message_read'),
    path('mail/messages/mark-all-read/', views.mail_mark_all_read, name='mail_mark_all_read'),
    path('mail/activities/', views.mail_activities_list, name='mail_activities_list'),
    path('mail/activities/types/', views.mail_activity_types, name='mail_activity_types'),
    path('mail/activities/create/', views.mail_activity_create, name='mail_activity_create'),
    path('mail/activities/<int:activity_id>/done/', views.mail_activity_done, name='mail_activity_done'),
    path('mail/activities/<int:activity_id>/cancel/', views.mail_activity_cancel, name='mail_activity_cancel'),

    # Technical > Models & Fields
    path('settings/technical/menu-items/', views.technical_menu_items, name='technical_menu_items'),
    path('settings/technical/menu-items/<int:menu_id>/', views.technical_menu_item_detail, name='technical_menu_item_detail'),
    path('settings/technical/models/new/', views.technical_model_create, name='technical_model_create'),
    path('settings/technical/models/', views.technical_models, name='technical_models'),
    path('settings/technical/models/<int:model_id>/', views.technical_model_detail, name='technical_model_detail'),
    path('settings/technical/fields/new/', views.technical_field_create, name='technical_field_create'),
    path('settings/technical/fields/', views.technical_fields, name='technical_fields'),
    path('settings/technical/fields/<int:field_id>/', views.technical_field_detail, name='technical_field_detail'),

    # Technical > Views
    path('settings/technical/views/new/', views.technical_view_create, name='technical_view_create'),
    path('settings/technical/views/', views.technical_views, name='technical_views'),
    path('settings/technical/views/<int:view_id>/', views.technical_view_detail, name='technical_view_detail'),

    # Technical > Sequences
    path('settings/technical/sequences/new/', views.technical_sequence_create, name='technical_sequence_create'),
    path('settings/technical/sequences/', views.technical_sequences, name='technical_sequences'),
    path('settings/technical/sequences/<int:sequence_id>/', views.technical_sequence_detail, name='technical_sequence_detail'),

    # Technical > Access Rights
    path('settings/technical/access-rights/new/', views.technical_access_right_create, name='technical_access_right_create'),
    path('settings/technical/access-rights/', views.technical_access_rights, name='technical_access_rights'),
    path('settings/technical/access-rights/<int:access_id>/', views.technical_access_right_detail, name='technical_access_right_detail'),

    # Technical > Record Rules
    path('settings/technical/record-rules/new/', views.technical_record_rule_create, name='technical_record_rule_create'),
    path('settings/technical/record-rules/', views.technical_record_rules, name='technical_record_rules'),
    path('settings/technical/record-rules/<int:rule_id>/', views.technical_record_rule_detail, name='technical_record_rule_detail'),

    # Technical > Actions
    path('settings/technical/actions/new/', views.technical_action_create, name='technical_action_create'),
    path('settings/technical/actions/', views.technical_actions, name='technical_actions'),
    path('settings/technical/actions/<int:action_id>/', views.technical_action_detail, name='technical_action_detail'),

    # Technical > ManyToMany Relations
    path('settings/technical/m2m/new/', views.technical_m2m_create, name='technical_m2m_create'),
    path('settings/technical/m2m/', views.technical_m2m, name='technical_m2m'),
    path('settings/technical/m2m/<int:m2m_id>/', views.technical_m2m_detail, name='technical_m2m_detail'),

    # Technical > Scheduled Actions (Cron Jobs)
    path('settings/technical/cron/new/', views.technical_cron_create, name='technical_cron_create'),
    path('settings/technical/cron/', views.technical_cron, name='technical_cron'),
    path('settings/technical/cron/<int:cron_id>/', views.technical_cron_detail, name='technical_cron_detail'),

    # Technical > Paper Formats
    path('settings/technical/paper-formats/new/', views.technical_paperformat_create, name='technical_paperformat_create'),
    path('settings/technical/paper-formats/', views.technical_paperformats, name='technical_paperformats'),
    path('settings/technical/paper-formats/<int:format_id>/', views.technical_paperformat_detail, name='technical_paperformat_detail'),

    # Technical > Reports
    path('settings/technical/reports/new/', views.technical_report_create, name='technical_report_create'),
    path('settings/technical/reports/', views.technical_reports, name='technical_reports'),
    path('settings/technical/reports/<int:report_id>/', views.technical_report_detail, name='technical_report_detail'),

    # Technical > Outgoing Mail Servers
    path('settings/technical/outgoing-mail/new/', views.technical_outgoing_mail_create, name='technical_outgoing_mail_create'),
    path('settings/technical/outgoing-mail/', views.technical_outgoing_mail, name='technical_outgoing_mail'),
    path('settings/technical/outgoing-mail/<int:server_id>/', views.technical_outgoing_mail_detail, name='technical_outgoing_mail_detail'),
    path('settings/technical/outgoing-mail/<int:server_id>/test-connection/', views.technical_outgoing_mail_test_connection, name='technical_outgoing_mail_test_connection'),
    path('settings/technical/outgoing-mail/test-connection-live/', views.technical_outgoing_mail_test_live, name='technical_outgoing_mail_test_live'),

    # Technical > Parameters (ir.config_parameter)
    path('settings/technical/parameters/new/', views.technical_parameter_create, name='technical_parameter_create'),
    path('settings/technical/parameters/', views.technical_parameters, name='technical_parameters'),
    path('settings/technical/parameters/<int:param_id>/', views.technical_parameter_detail, name='technical_parameter_detail'),

    # Technical > Logging & Diagnostics (ir.logging)
    path('settings/technical/logging/', views.technical_logging, name='technical_logging'),
    path('settings/technical/logging/<int:log_id>/', views.technical_log_detail, name='technical_log_detail'),
    path('settings/technical/logging/clear/', views.technical_logging_clear, name='technical_logging_clear'),

    # Generic many2one chip widget search (any model registered in IrModel)
    path('technical/relation-search/', views.relation_search, name='relation_search'),

    # Favorites (saved searches) -- Odoo ir.filters equivalent
    path('technical/filters/save/', views.save_filter, name='save_filter'),
    path('technical/filters/<int:filter_id>/set-default/', views.set_default_filter, name='set_default_filter'),
    path('technical/filters/<int:filter_id>/delete/', views.delete_filter, name='delete_filter'),
]