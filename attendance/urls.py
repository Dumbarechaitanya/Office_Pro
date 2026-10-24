from django.urls import path
from attendance import views

urlpatterns = [
    path('attendances/', views.attendance_list, name='attendance_list'),
    path('attendance/', views.attendance_list, name='attendance_home'),
    path('attendances/overview/', views.attendance_overview, name='attendance_overview'),
    path('attendances/new/', views.attendance_create, name='attendance_create'),
    path('attendances/<int:attendance_id>/', views.attendance_detail, name='attendance_detail'),
    path('attendances/<int:attendance_id>/delete/', views.attendance_delete, name='attendance_delete'),
    path('attendances/punch/', views.punch_toggle, name='attendance_punch_toggle'),
    path('attendances/reporting/pivot/', views.reporting_pivot, name='attendance_reporting_pivot'),
    path('attendances/reporting/time-off-ledger/', views.time_off_ledger, name='time_off_ledger'),
    path('attendances/management/absence-tracking/', views.absence_tracking, name='absence_tracking'),
    path('attendances/devices/', views.biometric_devices, name='biometric_devices'),
    path('attendances/devices/new/', views.biometric_device_create, name='biometric_device_create'),
    path('attendances/devices/<int:device_id>/', views.biometric_device_detail, name='biometric_device_detail'),
    path('attendances/devices/<int:device_id>/sync/', views.biometric_device_sync, name='biometric_device_sync'),
    path('attendances/devices/<int:device_id>/request-users/', views.biometric_device_request_users, name='biometric_device_request_users'),
    path('attendances/devices/<int:device_id>/auto-map/', views.biometric_device_auto_map, name='biometric_device_auto_map'),
    path('attendances/pending-reviews/', views.pending_reviews, name='attendance_pending_reviews'),
    path('attendances/settings/', views.attendance_settings, name='attendance_settings'),
    path('attendances/onboarding/', views.attendance_onboarding, name='attendance_onboarding'),
    path('attendances/overtime-rulesets/', views.overtime_rulesets, name='overtime_rulesets'),
    path('attendances/overtime-rulesets/<int:ruleset_id>/', views.overtime_ruleset_detail, name='overtime_ruleset_detail'),
    path('attendances/overtime-rulesets/<int:ruleset_id>/regenerate/', views.regenerate_overtimes, name='regenerate_overtimes'),
]
