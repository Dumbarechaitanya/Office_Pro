import json
from django.test import TestCase, Client
from django.urls import reverse
from base.models import ResUsers, ResCompany, ResGroups, ResUsersGroups
from employee.models import Department, Employee, OnboardingTemplate


class EmployeeModelTestCase(TestCase):
    def setUp(self):
        self.company = ResCompany.objects.create(name="Office Pro Architecture Ltd")
        self.dept = Department.objects.create(
            name="Structural Engineering",
            code="STR",
            color="#059669"
        )
        self.emp = Employee.objects.create(
            employee_code="EMP9001",
            name="Vikram Sharma",
            email="vikram.sharma@officepro.com",
            phone="+919876543210",
            department_rel=self.dept,
            department="Structural Engineering",
            job_title="Senior Structural Engineer",
            date_joined="2025-01-15",
            branch="Mumbai",
            employment_type="Full-Time",
            pan_number="ABCDE1234F",
            aadhaar_number="123456789012",
            hourly_cost=850.00,
            annual_ctc=1800000.00,
        )

    def test_employee_string_and_properties(self):
        self.assertEqual(str(self.emp), "Vikram Sharma (EMP9001)")
        self.assertEqual(self.emp.display_department, "Structural Engineering")
        self.assertEqual(self.emp.masked_pan, "ABXXXXX4F")
        self.assertEqual(self.emp.masked_aadhaar, "XXXX-XXXX-9012")

    def test_department_string_and_count(self):
        self.assertEqual(str(self.dept), "Structural Engineering")
        self.assertEqual(self.dept.total_members, 1)

    def test_onboarding_template_creation(self):
        tmpl = OnboardingTemplate.objects.create(
            name="Engineer Onboarding",
            department=self.dept,
            job_title="Associate Engineer",
            branch="Mumbai",
            timesheet_approver=self.emp,
            checklist_notes="Setup workstation, CAD licenses"
        )
        self.assertEqual(str(tmpl), "Engineer Onboarding")
        self.assertEqual(tmpl.timesheet_approver, self.emp)


class EmployeeViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.company = ResCompany.objects.create(name="Office Pro Ltd")
        self.dept = Department.objects.create(name="Design Studio", code="DES", color="#6366f1")

        # Admin user
        self.admin_user = ResUsers.objects.create(
            username="admin_test",
            email="admin@test.com",
            password_hash="testhash",
            company=self.company,
        )
        self.admin_group = ResGroups.objects.create(name="Administrator")
        ResUsersGroups.objects.create(user=self.admin_user, group=self.admin_group)

        # Regular user with Employee profile
        self.emp1 = Employee.objects.create(
            employee_code="EMP101",
            name="Alice Architect",
            email="alice@test.com",
            department_rel=self.dept,
            date_joined="2025-03-01",
            hourly_cost=700.00,
        )
        self.emp2 = Employee.objects.create(
            employee_code="EMP102",
            name="Bob Builder",
            email="bob@test.com",
            department_rel=self.dept,
            date_joined="2025-04-01",
            manager=self.emp1,
            hourly_cost=500.00,
        )
        self.regular_user = ResUsers.objects.create(
            username="bob_user",
            email="bob@test.com",
            password_hash="testhash",
            company=self.company,
            employee=self.emp2,
        )

        # Onboarding template
        self.template = OnboardingTemplate.objects.create(
            name="Architect Onboarding",
            department=self.dept,
            job_title="Architect",
            timesheet_approver=self.emp1,
            leave_approver_l1=self.emp1,
            expense_approver_l1=self.emp1,
        )

    def login_as(self, user):
        session = self.client.session
        session['user_id'] = user.id
        session.save()

    def test_anonymous_redirect(self):
        response = self.client.get(reverse('employee_list'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_employee_list_view_authenticated(self):
        self.login_as(self.regular_user)
        response = self.client.get(reverse('employee_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Alice Architect")
        self.assertContains(response, "Bob Builder")

    def test_employee_list_search_and_filter(self):
        self.login_as(self.admin_user)
        # Search query
        response = self.client.get(reverse('employee_list') + '?q=Alice')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Alice Architect")
        self.assertNotContains(response, "Bob Builder")

        # Department filter
        response = self.client.get(reverse('employee_list') + f'?department={self.dept.id}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['employees']), 2)

    def test_employee_detail_self_service(self):
        self.login_as(self.regular_user)
        # Can view own profile
        response = self.client.get(reverse('employee_detail', args=[self.emp2.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Bob Builder")

        # Cannot view another employee profile (redirected)
        response = self.client.get(reverse('employee_detail', args=[self.emp1.id]))
        self.assertEqual(response.status_code, 302)

    def test_employee_detail_admin_full_access(self):
        self.login_as(self.admin_user)
        response = self.client.get(reverse('employee_detail', args=[self.emp1.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Alice Architect")
        # CTC fields visible
        self.assertContains(response, "hourly_cost")

    def test_employee_create_by_admin(self):
        self.login_as(self.admin_user)
        response = self.client.post(reverse('employee_create'), {
            'name': 'Charlie Contractor',
            'employee_code': 'EMP103',
            'email': 'charlie@test.com',
            'date_joined': '2025-05-10',
            'department_id': str(self.dept.id),
            'job_title': 'Site Supervisor',
            'hourly_cost': '600.00',
            'annual_ctc': '1200000.00',
        })
        self.assertEqual(response.status_code, 302)
        new_emp = Employee.objects.filter(employee_code='EMP103').first()
        self.assertIsNotNone(new_emp)
        self.assertEqual(new_emp.name, 'Charlie Contractor')

    def test_department_views(self):
        self.login_as(self.admin_user)
        # Department list
        response = self.client.get(reverse('department_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Design Studio")

        # Create department
        response = self.client.post(reverse('department_create'), {
            'name': 'Urban Planning',
            'code': 'URB',
            'color': '#10b981',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Department.objects.filter(name='Urban Planning').exists())

    def test_org_chart_view(self):
        self.login_as(self.regular_user)
        response = self.client.get(reverse('employee_org_chart'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Alice Architect")
        self.assertContains(response, "Bob Builder")

    def test_onboarding_template_api(self):
        self.login_as(self.admin_user)
        response = self.client.get(reverse('employee_api_template_details', args=[self.template.id]))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['name'], "Architect Onboarding")
        self.assertEqual(data['timesheet_approver_id'], self.emp1.id)
