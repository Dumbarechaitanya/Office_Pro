from django.urls import path
from leave import views

urlpatterns = [
    # Calendar & Overview
    path('time-off/', views.leave_dashboard, name='leave_dashboard'),
    path('leave/', views.leave_dashboard, name='leave_home'),
    path('time-off/overview/', views.leave_dashboard, name='leave_overview'),
    
    # My Time
    path('time-off/my-time-off/', views.my_time_off, name='my_time_off'),
    path('time-off/my-allocations/', views.my_allocations, name='my_allocations'),
    
    # Management: Time Off Requests
    path('time-off/management/requests/', views.leave_management_requests, name='leave_management_requests'),
    path('time-off/request/new/', views.leave_request_create, name='leave_request_create'),
    path('time-off/request/<int:request_id>/', views.leave_request_detail, name='leave_request_detail'),
    path('time-off/request/<int:request_id>/action/', views.leave_request_action, name='leave_request_action'),
    
    # Management: Allocations
    path('time-off/management/allocations/', views.leave_management_allocations, name='leave_management_allocations'),
    path('time-off/allocation/new/', views.leave_allocation_create, name='leave_allocation_create'),
    path('time-off/allocation/<int:allocation_id>/', views.leave_allocation_detail, name='leave_allocation_detail'),
    path('time-off/allocation/<int:allocation_id>/action/', views.leave_allocation_action, name='leave_allocation_action'),
    
    # Reporting
    path('time-off/reporting/by-employee/', views.reporting_by_employee, name='leave_reporting_employee'),
    path('time-off/reporting/by-type/', views.reporting_by_type, name='leave_reporting_type'),
    
    # Configuration
    path('time-off/configuration/types/', views.configuration_types, name='leave_config_types'),
    path('time-off/configuration/types/new/', views.leave_type_create, name='leave_type_create'),
    path('time-off/configuration/types/<int:type_id>/', views.leave_type_detail, name='leave_type_detail'),
    path('time-off/configuration/mandatory-days/', views.configuration_mandatory_days, name='leave_config_mandatory_days'),
    path('time-off/configuration/mandatory-days/new/', views.mandatory_day_create, name='leave_mandatory_day_create'),
    path('time-off/configuration/mandatory-days/<int:day_id>/', views.mandatory_day_detail, name='leave_mandatory_day_detail'),
]
