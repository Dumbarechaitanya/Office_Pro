from django.contrib import admin
from employee.models import Department, Employee, OnboardingTemplate


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'manager', 'parent', 'is_active')
    search_fields = ('name', 'code')


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('employee_code', 'name', 'email', 'department', 'job_title', 'branch', 'is_active')
    search_fields = ('name', 'employee_code', 'email', 'job_title')
    list_filter = ('department', 'branch', 'employment_type', 'is_active')


@admin.register(OnboardingTemplate)
class OnboardingTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'department', 'job_title', 'employment_type', 'branch', 'is_active')
    search_fields = ('name', 'job_title')
