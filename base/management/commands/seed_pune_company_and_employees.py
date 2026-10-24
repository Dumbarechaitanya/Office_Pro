import os
from datetime import date, datetime, timedelta, time
from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from base.models import ResCompany, ResUsers, ResGroups, ResUsersGroups
from employee.models import Employee, Department
from attendance.models import Attendance


class Command(BaseCommand):
    help = "Seeds Pune HQ IT company (NexusWave Technologies), 6 departments, 45 diverse Indian employees, ResUsers accounts, and attendance logs."

    def handle(self, *args, **options):
        self.stdout.write("Seeding NexusWave Technologies and 45 Indian employees...")

        # 1. Company Setup
        company, _ = ResCompany.objects.get_or_create(
            name="NexusWave Technologies",
            defaults={
                'street': "Alpha Tower, Phase 1",
                'city': "Hinjawadi, Pune",
                'state': "Maharashtra",
                'zip_code': "411057",
                'country': "India",
                'email': "contact@nexuswave.in",
                'phone': "+91 20 6712 8000",
                'website': "https://nexuswave.in",
                'currency': "INR",
                'color': "#714b67",
                'is_active': True,
            }
        )
        self.stdout.write(f"Company: {company.name} ({company.city})")

        # 2. Departments Setup (6 Departments)
        dept_data = [
            ("Engineering & Technology", "ENG", "#0284c7"),
            ("Product & Design", "PRD", "#8b5cf6"),
            ("Human Resources & Talent", "HR", "#ec4899"),
            ("Sales & Business Development", "SLS", "#f59e0b"),
            ("Operations & Infrastructure", "OPS", "#10b981"),
            ("Finance & Accounts", "FIN", "#6366f1"),
        ]

        departments = {}
        for name, code, color in dept_data:
            dept, _ = Department.objects.get_or_create(
                name=name,
                defaults={'code': code, 'color': color, 'is_active': True}
            )
            departments[name] = dept

        # 3. 45 Diverse Indian Employees
        # Categories: Maharashtra/Marathi, North India, South India, East India
        employee_profiles = [
            # --- Maharashtra & Western India (22) ---
            ("Rohan Deshmukh", "Engineering & Technology", "VP of Engineering", "Male", "Married", "O+", "rohan.deshmukh@nexuswave.in", "+91 98231 10001", "ABCDE1001F", "452187901234", 3200000, 1600, date(2023, 1, 15), "Baner, Pune"),
            ("Tanvi Kulkarni", "Engineering & Technology", "Staff Software Engineer", "Female", "Single", "B+", "tanvi.kulkarni@nexuswave.in", "+91 98231 10002", "ABCDE1002F", "452187901235", 2400000, 1200, date(2023, 3, 1), "Aundh, Pune"),
            ("Aditya Joshi", "Engineering & Technology", "Senior Backend Architect", "Male", "Married", "A+", "aditya.joshi@nexuswave.in", "+91 98231 10003", "ABCDE1003F", "452187901236", 2100000, 1050, date(2023, 4, 10), "Kothrud, Pune"),
            ("Sneha Patil", "Engineering & Technology", "Senior Full Stack Engineer", "Female", "Single", "AB+", "sneha.patil@nexuswave.in", "+91 98231 10004", "ABCDE1004F", "452187901237", 1850000, 925, date(2023, 6, 12), "Wakad, Pune"),
            ("Nikhil Shinde", "Engineering & Technology", "Frontend Lead", "Male", "Single", "O+", "nikhil.shinde@nexuswave.in", "+91 98231 10005", "ABCDE1005F", "452187901238", 1750000, 875, date(2023, 7, 18), "Pimple Saudagar, Pune"),
            ("Aniket Gokhale", "Engineering & Technology", "DevOps & Cloud Engineer", "Male", "Single", "A-", "aniket.gokhale@nexuswave.in", "+91 98231 10006", "ABCDE1006F", "452187901239", 1600000, 800, date(2023, 9, 1), "Bavdhan, Pune"),
            ("Ritu Salunke", "Engineering & Technology", "Senior QA Automation Engineer", "Female", "Married", "B+", "ritu.salunke@nexuswave.in", "+91 98231 10007", "ABCDE1007F", "452187901240", 1450000, 725, date(2023, 10, 15), "Hinjawadi, Pune"),
            ("Swapnil Jagtap", "Engineering & Technology", "Backend Developer", "Male", "Single", "O+", "swapnil.jagtap@nexuswave.in", "+91 98231 10008", "ABCDE1008F", "452187901241", 1200000, 600, date(2024, 1, 8), "Pashan, Pune"),
            ("Radhika Sawant", "Engineering & Technology", "Database Administrator", "Female", "Married", "A+", "radhika.sawant@nexuswave.in", "+91 98231 10009", "ABCDE1009F", "452187901242", 1550000, 775, date(2024, 2, 20), "Shivaji Nagar, Pune"),
            ("Gaurav More", "Engineering & Technology", "Cloud Infrastructure Specialist", "Male", "Single", "B-", "gaurav.more@nexuswave.in", "+91 98231 10010", "ABCDE1010F", "452187901243", 1400000, 700, date(2024, 3, 15), "Viman Nagar, Pune"),
            ("Harshada Gaikwad", "Human Resources & Talent", "Head of Human Resources", "Female", "Married", "O+", "harshada.gaikwad@nexuswave.in", "+91 98231 10011", "ABCDE1011F", "452187901244", 2200000, 1100, date(2023, 2, 1), "Kalyani Nagar, Pune"),
            ("Chinmay Kadam", "Human Resources & Talent", "Lead Talent Acquisition", "Male", "Married", "A+", "chinmay.kadam@nexuswave.in", "+91 98231 10012", "ABCDE1012F", "452187901245", 1300000, 650, date(2023, 5, 10), "Hadapsar, Pune"),
            ("Sayali Thorat", "Human Resources & Talent", "HR Operations Specialist", "Female", "Single", "B+", "sayali.thorat@nexuswave.in", "+91 98231 10013", "ABCDE1013F", "452187901246", 950000, 475, date(2024, 1, 15), "Kothrud, Pune"),
            ("Varun Apte", "Finance & Accounts", "Head of Finance & Tax", "Male", "Married", "O+", "varun.apte@nexuswave.in", "+91 98231 10014", "ABCDE1014F", "452187901247", 2600000, 1300, date(2023, 1, 10), "Model Colony, Pune"),
            ("Shrikant Phadke", "Finance & Accounts", "Senior Corporate Accountant", "Male", "Married", "B+", "shrikant.phadke@nexuswave.in", "+91 98231 10015", "ABCDE1015F", "452187901248", 1400000, 700, date(2023, 6, 1), "Deccan, Pune"),
            ("Amol Bapat", "Finance & Accounts", "Financial Planning & Analyst", "Male", "Single", "A+", "amol.bapat@nexuswave.in", "+91 98231 10016", "ABCDE1016F", "452187901249", 1150000, 575, date(2024, 4, 1), "Karve Nagar, Pune"),
            ("Ketaki Chitale", "Product & Design", "Lead Product Designer (UI/UX)", "Female", "Single", "O+", "ketaki.chitale@nexuswave.in", "+91 98231 10017", "ABCDE1017F", "452187901250", 1900000, 950, date(2023, 3, 20), "Baner Pashan Link Rd, Pune"),
            ("Makarand Godbole", "Product & Design", "Principal Product Manager", "Male", "Married", "B+", "makarand.godbole@nexuswave.in", "+91 98231 10018", "ABCDE1018F", "452187901251", 2700000, 1350, date(2023, 2, 15), "Prabhat Road, Pune"),
            ("Priyanka Date", "Product & Design", "Senior Technical Scrum Master", "Female", "Married", "A+", "priyanka.date@nexuswave.in", "+91 98231 10019", "ABCDE1019F", "452187901252", 1650000, 825, date(2023, 8, 1), "Balewadi, Pune"),
            ("Digvijay Inamdar", "Operations & Infrastructure", "Director of IT Operations", "Male", "Married", "O+", "digvijay.inamdar@nexuswave.in", "+91 98231 10020", "ABCDE1020F", "452187901253", 2500000, 1250, date(2023, 1, 5), "Magarpatta City, Pune"),
            ("Bhushan Chavan", "Operations & Infrastructure", "Senior Systems Administrator", "Male", "Single", "B+", "bhushan.chavan@nexuswave.in", "+91 98231 10021", "ABCDE1021F", "452187901254", 1250000, 625, date(2023, 9, 15), "Chinchwad, Pune"),
            ("Pallavi Sathe", "Sales & Business Development", "Senior Enterprise Sales Manager", "Female", "Married", "A+", "pallavi.sathe@nexuswave.in", "+91 98231 10022", "ABCDE1022F", "452187901255", 2100000, 1050, date(2023, 4, 1), "Koregaon Park, Pune"),

            # --- North India (10) ---
            ("Aarav Sharma", "Engineering & Technology", "Principal Architect", "Male", "Married", "O+", "aarav.sharma@nexuswave.in", "+91 98110 20001", "ABCDE2001F", "652198101234", 3000000, 1500, date(2023, 2, 1), "Hinjawadi Phase 2, Pune"),
            ("Rohit Verma", "Engineering & Technology", "Senior Python / Django Lead", "Male", "Married", "B+", "rohit.verma@nexuswave.in", "+91 98110 20002", "ABCDE2002F", "652198101235", 1950000, 975, date(2023, 5, 15), "Baner, Pune"),
            ("Priya Singhania", "Product & Design", "Director of Product Management", "Female", "Single", "A+", "priya.singhania@nexuswave.in", "+91 98110 20003", "ABCDE2003F", "652198101236", 2900000, 1450, date(2023, 1, 10), "Kalyani Nagar, Pune"),
            ("Neha Kapoor", "Product & Design", "Product Marketing Lead", "Female", "Single", "AB+", "neha.kapoor@nexuswave.in", "+91 98110 20004", "ABCDE2004F", "652198101237", 1700000, 850, date(2023, 7, 1), "Viman Nagar, Pune"),
            ("Vikas Malhotra", "Sales & Business Development", "VP of Global Enterprise Sales", "Male", "Married", "O+", "vikas.malhotra@nexuswave.in", "+91 98110 20005", "ABCDE2005F", "652198101238", 3400000, 1700, date(2023, 1, 1), "Senapati Bapat Rd, Pune"),
            ("Anjali Rastogi", "Sales & Business Development", "Enterprise Account Director", "Female", "Married", "B+", "anjali.rastogi@nexuswave.in", "+91 98110 20006", "ABCDE2006F", "652198101239", 2200000, 1100, date(2023, 4, 15), "Aundh, Pune"),
            ("Rahul Bhatnagar", "Sales & Business Development", "Strategic Partnerships Manager", "Male", "Single", "A-", "rahul.bhatnagar@nexuswave.in", "+91 98110 20007", "ABCDE2007F", "652198101240", 1600000, 800, date(2023, 11, 1), "Wakad, Pune"),
            ("Deepak Mishra", "Operations & Infrastructure", "Cloud Security Engineer", "Male", "Single", "O+", "deepak.mishra@nexuswave.in", "+91 98110 20008", "ABCDE2008F", "652198101241", 1500000, 750, date(2024, 2, 1), "Pashan, Pune"),
            ("Meera Agarwal", "Finance & Accounts", "Chief Financial Officer (CFO)", "Female", "Married", "A+", "meera.agarwal@nexuswave.in", "+91 98110 20009", "ABCDE2009F", "652198101242", 4200000, 2100, date(2023, 1, 1), "Koregaon Park, Pune"),
            ("Nitin Saxena", "Finance & Accounts", "Billing & Statutory Auditor", "Male", "Married", "B+", "nitin.saxena@nexuswave.in", "+91 98110 20010", "ABCDE2010F", "652198101243", 1350000, 675, date(2023, 8, 15), "Baner, Pune"),

            # --- South India (8) ---
            ("Karthik Subramanian", "Engineering & Technology", "Staff Backend Architect", "Male", "Married", "O+", "karthik.subramanian@nexuswave.in", "+91 98440 30001", "ABCDE3001F", "782145601234", 2800000, 1400, date(2023, 2, 1), "Hinjawadi Phase 1, Pune"),
            ("Divya Ramanathan", "Engineering & Technology", "Lead AI / ML Engineer", "Female", "Single", "B+", "divya.ramanathan@nexuswave.in", "+91 98440 30002", "ABCDE3002F", "782145601235", 2300000, 1150, date(2023, 6, 1), "Wakad, Pune"),
            ("Arvind Natarajan", "Engineering & Technology", "Senior Big Data Engineer", "Male", "Married", "A+", "arvind.natarajan@nexuswave.in", "+91 98440 30003", "ABCDE3003F", "782145601236", 1900000, 950, date(2023, 9, 1), "Baner, Pune"),
            ("Shweta Venkataraman", "Engineering & Technology", "DevSecOps Specialist", "Female", "Single", "O+", "shweta.venkat@nexuswave.in", "+91 98440 30004", "ABCDE3004F", "782145601237", 1750000, 875, date(2024, 1, 10), "Pashan, Pune"),
            ("Manoj Kumar", "Engineering & Technology", "Senior Mobile Lead (Android/iOS)", "Male", "Married", "B-", "manoj.kumar@nexuswave.in", "+91 98440 30005", "ABCDE3005F", "782145601238", 1850000, 925, date(2023, 5, 20), "Bavdhan, Pune"),
            ("Deepa Narayanan", "Product & Design", "Senior UI/UX Researcher", "Female", "Single", "A+", "deepa.narayanan@nexuswave.in", "+91 98440 30006", "ABCDE3006F", "782145601239", 1550000, 775, date(2023, 10, 1), "Kothrud, Pune"),
            ("Ashwin Krishnan", "Operations & Infrastructure", "IT Security Lead", "Male", "Single", "O+", "ashwin.krishnan@nexuswave.in", "+91 98440 30007", "ABCDE3007F", "782145601240", 1650000, 825, date(2023, 7, 15), "Aundh, Pune"),
            ("Lakshmi Sundaram", "Operations & Infrastructure", "Office & Facilities Manager", "Female", "Married", "B+", "lakshmi.sundaram@nexuswave.in", "+91 98440 30008", "ABCDE3008F", "782145601241", 1100000, 550, date(2023, 3, 1), "Hinjawadi, Pune"),

            # --- East India / Bengal (5) ---
            ("Sagnik Banerjee", "Engineering & Technology", "Tech Lead - Platform Engineering", "Male", "Married", "O+", "sagnik.banerjee@nexuswave.in", "+91 98300 40001", "ABCDE4001F", "892156701234", 2250000, 1125, date(2023, 3, 15), "Viman Nagar, Pune"),
            ("Ananya Chatterjee", "Product & Design", "Senior Product Designer", "Female", "Single", "A+", "ananya.chatterjee@nexuswave.in", "+91 98300 40002", "ABCDE4002F", "892156701235", 1600000, 800, date(2023, 8, 10), "Kalyani Nagar, Pune"),
            ("Debashis Roy", "Engineering & Technology", "Full Stack Developer", "Male", "Single", "B+", "debashis.roy@nexuswave.in", "+91 98300 40003", "ABCDE4003F", "892156701236", 1300000, 650, date(2024, 2, 1), "Wakad, Pune"),
            ("Payel Sen", "Sales & Business Development", "Regional Sales Manager", "Female", "Single", "O+", "payel.sen@nexuswave.in", "+91 98300 40004", "ABCDE4004F", "892156701237", 1700000, 850, date(2023, 11, 15), "Baner, Pune"),
            ("Subhashish Mukherjee", "Operations & Infrastructure", "Network Operations Lead", "Male", "Married", "A-", "subhashish.m@nexuswave.in", "+91 98300 40005", "ABCDE4005F", "892156701238", 1450000, 725, date(2023, 6, 1), "Hinjawadi Phase 3, Pune"),
        ]

        # Clean existing dummy employee 1 if Johnathan Doe
        Employee.objects.filter(name="Johnathan Doe").delete()

        admin_group = ResGroups.objects.filter(name='Administrator').first()
        user_group = ResGroups.objects.filter(name='User').first()
        hashed_pwd = make_password('123')

        created_employees = []
        for idx, (name, dept_name, job_title, gender, marital, blood, email, phone, pan, aadhaar, ctc, hourly, joined, addr) in enumerate(employee_profiles, start=1):
            emp_code = f"EMP{idx:03d}"
            dept_obj = departments.get(dept_name)

            emp, created = Employee.objects.update_or_create(
                employee_code=emp_code,
                defaults={
                    'name': name,
                    'email': email,
                    'phone': phone,
                    'department': dept_name,
                    'department_rel': dept_obj,
                    'job_title': job_title,
                    'date_joined': joined,
                    'gender': gender,
                    'marital_status': marital,
                    'blood_group': blood,
                    'pan_number': pan,
                    'aadhaar_number': aadhaar,
                    'employment_type': 'Full-Time',
                    'branch': 'Pune HQ (Hinjawadi)',
                    'current_address': addr,
                    'current_city': 'Pune',
                    'current_state': 'Maharashtra',
                    'current_pincode': '411057',
                    'permanent_address': addr,
                    'permanent_city': 'Pune',
                    'permanent_state': 'Maharashtra',
                    'permanent_pincode': '411057',
                    'bank_name': 'HDFC Bank Ltd',
                    'bank_account_number': f"501002345{idx:04d}",
                    'ifsc_code': 'HDFC0001024',
                    'bank_branch': 'Hinjawadi Phase 1, Pune',
                    'annual_ctc': ctc,
                    'hourly_cost': hourly,
                    'is_active': True,
                }
            )
            created_employees.append(emp)

            # Create or link ResUsers
            user_obj, u_created = ResUsers.objects.update_or_create(
                username=email,
                defaults={
                    'email': email,
                    'password_hash': hashed_pwd,
                    'company': company,
                    'employee': emp,
                    'is_active': True,
                }
            )
            if user_group:
                ResUsersGroups.objects.get_or_create(user=user_obj, group=user_group)

        self.stdout.write(f"Created {len(created_employees)} employees and users.")

        # Update Department managers to senior leads
        departments["Engineering & Technology"].manager = created_employees[0]  # Rohan Deshmukh
        departments["Product & Design"].manager = created_employees[17]       # Makarand Godbole
        departments["Human Resources & Talent"].manager = created_employees[10] # Harshada Gaikwad
        departments["Sales & Business Development"].manager = created_employees[26] # Vikas Malhotra
        departments["Operations & Infrastructure"].manager = created_employees[19] # Digvijay Inamdar
        departments["Finance & Accounts"].manager = created_employees[30]      # Meera Agarwal
        for d in departments.values():
            d.save()

        # Update admin user 1 to be linked to Rohan Deshmukh and company NexusWave
        admin_user = ResUsers.objects.filter(id=1).first()
        if admin_user:
            admin_user.company = company
            admin_user.employee = created_employees[0]
            admin_user.save()
            if admin_group:
                ResUsersGroups.objects.get_or_create(user=admin_user, group=admin_group)

        # 4. Seed Attendance Records
        # Clean old attendance
        Attendance.objects.all().delete()

        today = date(2026, 10, 23)

        # A) Today's Attendance logs (23 records matching Screenshot 1)
        # Specific timestamps matching the pattern from Screenshot 1:
        # In Screenshot 1:
        # 1. Check in 11:32 AM, Check Out 8:09 PM -> Worked 07:57, Extra 00:00
        # 2. Check in 11:14 AM, Check Out 6:50 PM -> Worked 06:56, Extra 00:00
        # 3. Check in 10:39 AM, Check Out None    -> Active Green (Worked 00:00)
        # 4. Check in 10:29 AM, Check Out 7:50 PM -> Worked 08:41, Extra 00:21
        # 5. Check in 10:28 AM, Check Out 7:08 PM -> Worked 08:00, Extra 00:00
        # 6. Check in 10:25 AM, Check Out 7:25 PM -> Worked 08:20, Extra 00:00
        # 7. Check in 10:25 AM, Check Out None    -> Active Green
        # 8. Check in 10:25 AM, Check Out None    -> Active Green
        # 9. Check in 10:25 AM, Check Out None    -> Active Green
        # 10. Check in 10:25 AM, Check Out 8:19 PM -> Worked 09:14, Extra 00:54
        # 11. Check in 10:19 AM, Check Out 7:29 PM -> Worked 08:30, Extra 00:10
        # 12. Check in 10:16 AM, Check Out 7:29 PM -> Worked 08:34, Extra 00:14
        # ... and more for 23 total records today
        today_punch_specs = [
            (time(11, 32), time(20, 9), "Biometric", "Biometric"),
            (time(11, 14), time(18, 50), "Biometric", "Biometric"),
            (time(10, 39), None, "Biometric", None),  # Active green
            (time(10, 29), time(19, 50), "Biometric", "Biometric"),
            (time(10, 28), time(19, 8), "Biometric", "Biometric"),
            (time(10, 25), time(19, 25), "Biometric", "Biometric"),
            (time(10, 25), None, "Biometric", None),  # Active green
            (time(10, 25), None, "Biometric", None),  # Active green
            (time(10, 25), None, "Biometric", None),  # Active green
            (time(10, 25), time(20, 19), "Biometric", "Biometric"),
            (time(10, 19), time(19, 29), "Biometric", "Biometric"),
            (time(10, 16), time(19, 29), "Biometric", "Biometric"),
            (time(10, 12), time(19, 15), "Biometric", "Biometric"),
            (time(10, 10), time(19, 5), "Biometric", "Biometric"),
            (time(10, 5),  time(18, 55), "Biometric", "Biometric"),
            (time(10, 0),  time(19, 2), "Biometric", "Biometric"),
            (time(9, 58),  time(18, 45), "Biometric", "Biometric"),
            (time(9, 55),  None, "Biometric", None),  # Active green
            (time(9, 50),  time(18, 30), "Biometric", "Biometric"),
            (time(9, 45),  time(18, 20), "Biometric", "Biometric"),
            (time(9, 40),  time(18, 15), "Biometric", "Biometric"),
            (time(9, 35),  time(18, 5), "Biometric", "Biometric"),
            (time(9, 30),  time(18, 0), "Biometric", "Biometric"),
        ]

        today_attendances = []
        for i, (t_in, t_out, mode_in, mode_out) in enumerate(today_punch_specs):
            emp = created_employees[i]
            dt_in = timezone.make_aware(datetime.combine(today, t_in)) if t_in else None
            dt_out = timezone.make_aware(datetime.combine(today, t_out)) if t_out else None

            att = Attendance.objects.create(
                employee=emp,
                date=today,
                check_in=dt_in,
                check_out=dt_out,
                status='Present',
                input_mode_in=mode_in,
                input_mode_out=mode_out or '',
                is_active=True
            )
            today_attendances.append(att)

        self.stdout.write(f"Created {len(today_attendances)} attendance records for today (Oct 23).")

        # B) Historical logs for past 3 months (July, August, September, and earlier October 2026)
        # To populate Screenshot 4 (Pivot) and Screenshot 5 (Time Off Ledger)
        history_attendances = []
        cur_date = date(2026, 7, 1)
        end_date = date(2026, 10, 22)

        while cur_date <= end_date:
            # Mon-Fri are working days (0=Mon, 4=Fri)
            if cur_date.weekday() < 5:
                # Seed records for all 45 employees
                for emp_idx, emp in enumerate(created_employees):
                    # Introduce realistic absences & variances based on emp and day
                    day_hash = (cur_date.day * 13 + cur_date.month * 37 + emp.id * 17) % 100

                    if day_hash < 6:
                        # Absent day
                        att = Attendance(
                            employee=emp,
                            date=cur_date,
                            check_in=None,
                            check_out=None,
                            status='Absent',
                            input_mode_in='',
                            input_mode_out='',
                            is_active=True
                        )
                        history_attendances.append(att)
                    else:
                        # Worked day
                        in_minute = 10 + (day_hash % 40)
                        out_minute = (day_hash * 3) % 50
                        work_hours = 8 + (day_hash % 2)

                        t_in = time(9 + (in_minute // 60), in_minute % 60)
                        t_out = time(17 + work_hours - 8, out_minute)

                        dt_in = timezone.make_aware(datetime.combine(cur_date, t_in))
                        dt_out = timezone.make_aware(datetime.combine(cur_date, t_out))

                        att = Attendance(
                            employee=emp,
                            date=cur_date,
                            check_in=dt_in,
                            check_out=dt_out,
                            status='Present',
                            input_mode_in='Biometric',
                            input_mode_out='Biometric',
                            is_active=True
                        )
                        history_attendances.append(att)

            cur_date += timedelta(days=1)

        Attendance.objects.bulk_create(history_attendances, batch_size=500)
        self.stdout.write(f"Bulk seeded {len(history_attendances)} historical attendance records across July-October 2026.")
        self.stdout.write(self.style.SUCCESS("Seeding completed successfully!"))
