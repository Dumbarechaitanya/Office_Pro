from django.core.management.base import BaseCommand
from django.db import transaction
from employee.models import Department, Employee


class Command(BaseCommand):
    help = "Sets up IT company department hierarchy with sub-teams under Engineering and eliminates duplicate departments."

    def handle(self, *args, **options):
        with transaction.atomic():
            self.stdout.write("1. Cleaning up duplicate empty departments (IDs 1-5)...")
            Department.objects.filter(id__in=[1, 2, 3, 4, 5]).delete()

            self.stdout.write("2. Standardizing macro departments...")
            # Engineering (ID 6)
            eng, _ = Department.objects.get_or_create(id=6, defaults={'name': 'Engineering', 'code': 'ENG'})
            eng.name = 'Engineering'
            eng.code = 'ENG'
            eng.color = '#0284c7'
            eng.parent = None
            try:
                eng.manager = Employee.objects.get(id=2)  # Rohan Deshmukh
            except Employee.DoesNotExist:
                pass
            eng.save()

            # Human Resources (ID 8)
            hr, _ = Department.objects.get_or_create(id=8, defaults={'name': 'Human Resources', 'code': 'HR'})
            hr.name = 'Human Resources'
            hr.code = 'HR'
            hr.color = '#ea580c'
            hr.parent = None
            try:
                hr.manager = Employee.objects.get(id=12)  # Harshada Gaikwad
            except Employee.DoesNotExist:
                pass
            hr.save()

            # Finance & Accounts (ID 11)
            fin, _ = Department.objects.get_or_create(id=11, defaults={'name': 'Finance & Accounts', 'code': 'FIN'})
            fin.name = 'Finance & Accounts'
            fin.code = 'FIN'
            fin.color = '#10b981'
            fin.parent = None
            try:
                fin.manager = Employee.objects.get(id=32)  # Meera Agarwal
            except Employee.DoesNotExist:
                pass
            fin.save()

            # Sales & Marketing (ID 9)
            sls, _ = Department.objects.get_or_create(id=9, defaults={'name': 'Sales & Marketing', 'code': 'SLS'})
            sls.name = 'Sales & Marketing'
            sls.code = 'SLS'
            sls.color = '#f59e0b'
            sls.parent = None
            try:
                sls.manager = Employee.objects.get(id=28)  # Vikas Malhotra
            except Employee.DoesNotExist:
                pass
            sls.save()

            # Product & Design (ID 7)
            prd, _ = Department.objects.get_or_create(id=7, defaults={'name': 'Product & Design', 'code': 'PRD'})
            prd.name = 'Product & Design'
            prd.code = 'PRD'
            prd.color = '#8b5cf6'
            prd.parent = None
            try:
                prd.manager = Employee.objects.get(id=26)  # Priya Singhania
            except Employee.DoesNotExist:
                pass
            prd.save()

            # Operations & Infrastructure (ID 10)
            ops, _ = Department.objects.get_or_create(id=10, defaults={'name': 'Operations & Infrastructure', 'code': 'OPS'})
            ops.name = 'Operations & Infrastructure'
            ops.code = 'OPS'
            ops.color = '#06b6d4'
            ops.parent = None
            try:
                ops.manager = Employee.objects.get(id=21)  # Digvijay Inamdar
            except Employee.DoesNotExist:
                pass
            ops.save()

            self.stdout.write("3. Creating technical sub-teams under Engineering...")
            sub_teams = [
                ('Java', 'ENG-JAVA', '#f97316', 3),     # Tanvi Kulkarni
                ('Python', 'ENG-PY', '#3b82f6', 25),    # Rohit Verma
                ('QA', 'ENG-QA', '#14b8a6', 8),         # Ritu Salunke
                ('DevOps', 'ENG-OPS', '#6366f1', 7),    # Aniket Gokhale
                ('UI/UX', 'ENG-UI', '#ec4899', 6),      # Nikhil Shinde
                ('AI & Data', 'ENG-AI', '#8b5cf6', 35), # Divya Ramanathan
            ]

            team_objs = {}
            for t_name, t_code, t_color, t_mgr_id in sub_teams:
                team, created = Department.objects.get_or_create(
                    name=t_name,
                    defaults={'code': t_code, 'color': t_color, 'parent': eng}
                )
                team.code = t_code
                team.color = t_color
                team.parent = eng
                try:
                    team.manager = Employee.objects.get(id=t_mgr_id)
                except Employee.DoesNotExist:
                    pass
                team.save()
                team_objs[t_name] = team
                self.stdout.write(f"   - {t_name} (Code: {t_code}, Parent: Engineering)")

            self.stdout.write("4. Assigning engineering staff to sub-teams...")
            # Java Team (Tanvi Kulkarni, Karthik Subramanian, Sneha Patil, Sagnik Banerjee)
            java_ids = [3, 5, 34, 42]
            Employee.objects.filter(id__in=java_ids).update(
                department='Java',
                department_rel=team_objs['Java']
            )

            # Python Team (Rohit Verma, Aditya Joshi, Swapnil Jagtap, Debashis Roy)
            py_ids = [25, 4, 9, 44]
            Employee.objects.filter(id__in=py_ids).update(
                department='Python',
                department_rel=team_objs['Python']
            )

            # QA Team (Ritu Salunke)
            qa_ids = [8]
            Employee.objects.filter(id__in=qa_ids).update(
                department='QA',
                department_rel=team_objs['QA']
            )

            # DevOps Team (Aniket Gokhale, Gaurav More, Shweta Venkataraman, Radhika Sawant)
            devops_ids = [7, 10, 11, 37]
            Employee.objects.filter(id__in=devops_ids).update(
                department='DevOps',
                department_rel=team_objs['DevOps']
            )

            # UI/UX Engineering Team (Nikhil Shinde, Manoj Kumar)
            ui_ids = [6, 38]
            Employee.objects.filter(id__in=ui_ids).update(
                department='UI/UX',
                department_rel=team_objs['UI/UX']
            )

            # AI & Data Team (Divya Ramanathan, Arvind Natarajan)
            ai_ids = [35, 36]
            Employee.objects.filter(id__in=ai_ids).update(
                department='AI & Data',
                department_rel=team_objs['AI & Data']
            )

            # Engineering Leadership (Rohan Deshmukh, Aarav Sharma)
            eng_leadership = [2, 24]
            Employee.objects.filter(id__in=eng_leadership).update(
                department='Engineering',
                department_rel=eng
            )

            # Update other macro departments
            Employee.objects.filter(department_rel_id=8).update(department='Human Resources')
            Employee.objects.filter(department_rel_id=11).update(department='Finance & Accounts')
            Employee.objects.filter(department_rel_id=9).update(department='Sales & Marketing')
            Employee.objects.filter(department_rel_id=7).update(department='Product & Design')
            Employee.objects.filter(department_rel_id=10).update(department='Operations & Infrastructure')

            self.stdout.write(self.style.SUCCESS("IT Department hierarchy successfully configured with 0 duplicates!"))
