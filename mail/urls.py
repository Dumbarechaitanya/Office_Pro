from django.urls import path
from mail import views

urlpatterns = [
    # Webmail Client Interface
    path('mail/app/', views.mail_app, name='mail_app'),
    path('mail/app/<str:folder>/', views.mail_app, name='mail_app_folder'),

    # REST APIs
    path('mail/api/emails/', views.mail_api_emails, name='mail_api_emails'),
    path('mail/api/emails/<int:email_id>/', views.mail_api_email_detail, name='mail_api_email_detail'),
    path('mail/api/compose/', views.mail_api_compose, name='mail_api_compose'),
    path('mail/api/reply/<int:email_id>/', views.mail_api_reply, name='mail_api_reply'),
    path('mail/api/star/<int:email_id>/', views.mail_api_star_toggle, name='mail_api_star_toggle'),
    path('mail/api/batch-action/', views.mail_api_batch_action, name='mail_api_batch_action'),
    path('mail/api/upload-attachment/', views.mail_api_attachment_upload, name='mail_api_attachment_upload'),
]
