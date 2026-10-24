from django.urls import path
from employee import views

urlpatterns = [
    # Employee Directory
    path('employees/', views.employee_list, name='employee_list'),
    path('employee/', views.employee_list, name='employee_home'),
    path('employees/new/', views.employee_create, name='employee_create'),
    path('employees/<int:emp_id>/', views.employee_detail, name='employee_detail'),

    # Organization & Departments
    path('employees/departments/', views.department_list, name='department_list'),
    path('employees/departments/new/', views.department_create, name='department_create'),
    path('employees/departments/<int:dept_id>/', views.department_detail, name='department_detail'),

    # Visual Org Chart
    path('employees/org-chart/', views.employee_org_chart, name='employee_org_chart'),

    # Onboarding Templates
    path('employees/onboarding-templates/', views.onboarding_templates, name='employee_onboarding_templates'),
    path('employees/onboarding-templates/new/', views.onboarding_template_create, name='employee_onboarding_template_create'),
    path('employees/onboarding-templates/<int:template_id>/', views.onboarding_template_detail, name='employee_onboarding_template_detail'),
    # Configuration Views
    path('employees/configuration/locations/', views.employee_config_locations, name='employee_config_locations'),
    path('employees/configuration/schedules/', views.employee_config_schedules, name='employee_config_schedules'),
    path('employees/configuration/departure-reasons/', views.employee_config_departure_reasons, name='employee_config_departure_reasons'),
    path('employees/configuration/skills/', views.employee_config_skills, name='employee_config_skills'),
]

