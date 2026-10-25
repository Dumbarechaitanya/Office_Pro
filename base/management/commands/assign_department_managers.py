"""
Assign department managers and their respective subordinate assignees.
Matches the requested enterprise organizational hierarchy:
- Aarav Sharma (4) [Engineering & Technology]
- Divya Ramanathan (4) [Engineering & Technology]
- Nikhil Shinde (3-4) [Engineering & Technology]
- Sagnik Banerjee (3) [Engineering & Technology]
- Amol Bapat (4) [Finance & Accounts]
- Aditya Joshi (3) [Human Resources & Talent]
- Ashwin Krishnan (2) [Operations & Infrastructure]
- Digvijay Inamdar (2) [Operations & Infrastructure]
- Ananya Chatterjee (3) [Product & Design]
- Neha Kapoor (3) [Product & Design]
- Anjali Rastogi (3) [Sales & Business Development]
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from employee.models import Employee, Department


class Command(BaseCommand):
    help = 'Assigns department manager positions and links subordinate assignees.'

    @transaction.atomic
    def handle(self, *args, **options):
        # 1. Helper to find employee by partial name
        def get_emp(query):
            return Employee.objects.filter(name__icontains=query, is_active=True).first()

        def set_hierarchy(manager, subordinates, dept_name=None):
            if not manager:
                self.stdout.write(self.style.ERROR(f"Manager not found for: {dept_name}"))
                return
            count = 0
            for sub in subordinates:
                if sub and sub.id != manager.id:
                    sub.manager = manager
                    sub.leave_approver_l1 = manager
                    sub.timesheet_approver = manager
                    sub.save(update_fields=['manager', 'leave_approver_l1', 'timesheet_approver', 'updated_at'])
                    count += 1
            self.stdout.write(self.style.SUCCESS(f"Assigned {count} subordinate(s) to manager: {manager.name}"))

        # --- 1. FINANCE & ACCOUNTS (Amol Bapat - 4 assignees) ---
        mgr_amol = get_emp('Amol Bapat')
        subs_amol = [
            get_emp('Varun Apte'),
            get_emp('Shrikant Phadke'),
            get_emp('Meera Agarwal'),
            get_emp('Nitin Saxena'),
        ]
        set_hierarchy(mgr_amol, subs_amol, 'Finance & Accounts')
        dept_fin = Department.objects.filter(name__icontains='Finance').first()
        if dept_fin and mgr_amol:
            dept_fin.manager = mgr_amol
            dept_fin.save(update_fields=['manager', 'updated_at'])

        # --- 2. HUMAN RESOURCES & TALENT (Aditya Joshi - 3 assignees) ---
        mgr_aditya = get_emp('Aditya Joshi')
        subs_aditya = [
            get_emp('Harshada Gaikwad'),
            get_emp('Chinmay Kadam'),
            get_emp('Sayali Thorat'),
        ]
        set_hierarchy(mgr_aditya, subs_aditya, 'Human Resources & Talent')
        dept_hr = Department.objects.filter(name__icontains='Human Resources').first()
        if dept_hr and mgr_aditya:
            dept_hr.manager = mgr_aditya
            dept_hr.save(update_fields=['manager', 'updated_at'])

        # --- 3. OPERATIONS & INFRASTRUCTURE ---
        # Ashwin Krishnan (2 assignees)
        mgr_ashwin = get_emp('Ashwin Krishnan')
        subs_ashwin = [
            get_emp('Deepak Mishra'),
            get_emp('Bhushan Chavan'),
        ]
        set_hierarchy(mgr_ashwin, subs_ashwin, 'Operations (Security)')

        # Digvijay Inamdar (2 assignees)
        mgr_digvijay = get_emp('Digvijay Inamdar')
        subs_digvijay = [
            get_emp('Subhashish Mukherjee'),
            get_emp('Lakshmi Sundaram'),
        ]
        set_hierarchy(mgr_digvijay, subs_digvijay, 'Operations (Infrastructure)')
        dept_ops = Department.objects.filter(name__icontains='Operations').first()
        if dept_ops and mgr_digvijay:
            dept_ops.manager = mgr_digvijay
            dept_ops.save(update_fields=['manager', 'updated_at'])

        # --- 4. PRODUCT & DESIGN ---
        # Ananya Chatterjee (3 assignees - Design & Research)
        mgr_ananya = get_emp('Ananya Chatterjee')
        subs_ananya = [
            get_emp('Deepa Narayanan'),
            get_emp('Ketaki Chitale'),
            get_emp('Priyanka Date'),
        ]
        set_hierarchy(mgr_ananya, subs_ananya, 'Product Design')

        # Neha Kapoor (3 assignees - Product Management & Sales Strategy)
        mgr_neha = get_emp('Neha Kapoor')
        subs_neha = [
            get_emp('Makarand Godbole'),
            get_emp('Priya Singhania'),
            get_emp('Vikas Malhotra'),
        ]
        set_hierarchy(mgr_neha, subs_neha, 'Product Management')
        dept_prd = Department.objects.filter(name__icontains='Product').first()
        if dept_prd and mgr_ananya:
            dept_prd.manager = mgr_ananya
            dept_prd.save(update_fields=['manager', 'updated_at'])

        # --- 5. SALES & BUSINESS DEVELOPMENT (Anjali Rastogi - 3 assignees) ---
        mgr_anjali = get_emp('Anjali Rastogi')
        subs_anjali = [
            get_emp('Pallavi Sathe'),
            get_emp('Rahul Bhatnagar'),
            get_emp('Payel Sen'),
        ]
        set_hierarchy(mgr_anjali, subs_anjali, 'Sales & Business Development')
        dept_sales = Department.objects.filter(name__icontains='Sales').first()
        if dept_sales and mgr_anjali:
            dept_sales.manager = mgr_anjali
            dept_sales.save(update_fields=['manager', 'updated_at'])

        # --- 6. ENGINEERING & TECHNOLOGY ---
        rohan = get_emp('Rohan Deshmukh')  # VP of Engineering
        mgr_aarav = get_emp('Aarav Sharma')
        mgr_divya = get_emp('Divya Ramanathan')
        mgr_nikhil = get_emp('Nikhil Shinde')
        mgr_sagnik = get_emp('Sagnik Banerjee')

        # 4 Managers report to VP Rohan Deshmukh
        if rohan:
            for em in [mgr_aarav, mgr_divya, mgr_nikhil, mgr_sagnik]:
                if em:
                    em.manager = rohan
                    em.leave_approver_l1 = rohan
                    em.timesheet_approver = rohan
                    em.save(update_fields=['manager', 'leave_approver_l1', 'timesheet_approver', 'updated_at'])

        # Aarav Sharma (4 assignees: Architecture & Data Core)
        subs_aarav = [
            get_emp('Karthik Subramanian'),
            get_emp('Arvind Natarajan'),
            get_emp('Radhika Sawant'),
            get_emp('Tanvi Kulkarni'),
        ]
        set_hierarchy(mgr_aarav, subs_aarav, 'Engineering - Architecture')

        # Divya Ramanathan (4 assignees: AI/ML & Core Applications)
        subs_divya = [
            get_emp('Rohit Verma'),
            get_emp('Debashis Roy'),
            get_emp('Swapnil Jagtap'),
            get_emp('Sneha Patil'),
        ]
        set_hierarchy(mgr_divya, subs_divya, 'Engineering - AI & Backend')

        # Nikhil Shinde (3 assignees: Frontend, QA & Mobile)
        subs_nikhil = [
            get_emp('Manoj Kumar'),
            get_emp('Ritu Salunke'),
            get_emp('Gaurav More'),
        ]
        set_hierarchy(mgr_nikhil, subs_nikhil, 'Engineering - Frontend & Mobile')

        # Sagnik Banerjee (2 assignees: Platform, Cloud & DevSecOps)
        subs_sagnik = [
            get_emp('Aniket Gokhale'),
            get_emp('Shweta Venkataraman'),
        ]
        set_hierarchy(mgr_sagnik, subs_sagnik, 'Engineering - Platform & Cloud')

        dept_eng = Department.objects.filter(name__icontains='Engineering').first()
        if dept_eng and rohan:
            dept_eng.manager = rohan
            dept_eng.save(update_fields=['manager', 'updated_at'])

        # For all engineering subordinates, set Rohan as leave_approver_l2 (2-tier workflow)
        if rohan:
            Employee.objects.filter(
                department__icontains='Engineering',
                is_active=True
            ).exclude(id=rohan.id).update(leave_approver_l2=rohan)

        self.stdout.write(self.style.SUCCESS("All department manager positions and subordinate assignees updated successfully!"))
