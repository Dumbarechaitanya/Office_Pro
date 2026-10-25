import os
from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = "Ensures PostgreSQL database schema compatibility by guaranteeing all required tables and columns exist."

    def handle(self, *args, **options):
        self.stdout.write("Checking and ensuring database schema compatibility...")

        ddl_statements = [
            # 0. Trigger helper
            """
            CREATE OR REPLACE FUNCTION set_updated_at()
            RETURNS TRIGGER AS $$
            BEGIN
                NEW.updated_at = NOW();
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;
            """,

            # 1. res_company table
            """
            CREATE TABLE IF NOT EXISTS res_company (
                id SERIAL PRIMARY KEY,
                name VARCHAR(150) NOT NULL,
                email VARCHAR(150),
                phone VARCHAR(20),
                address TEXT,
                street VARCHAR(255),
                city VARCHAR(100),
                state VARCHAR(100),
                zip_code VARCHAR(20),
                country VARCHAR(100) DEFAULT 'India',
                website VARCHAR(255),
                currency VARCHAR(10) DEFAULT 'INR',
                color VARCHAR(20) DEFAULT '#0284c7',
                logo_url VARCHAR(255),
                is_active BOOLEAN NOT NULL DEFAULT TRUE,
                created_at TIMESTAMP NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMP NOT NULL DEFAULT NOW()
            );
            """,

            # 2. res_users table
            """
            CREATE TABLE IF NOT EXISTS res_users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(100) NOT NULL UNIQUE,
                email VARCHAR(150) NOT NULL UNIQUE,
                password_hash VARCHAR(255) NOT NULL,
                company_id INTEGER REFERENCES res_company(id) ON DELETE SET NULL,
                employee_id INTEGER,
                is_active BOOLEAN NOT NULL DEFAULT TRUE,
                last_login TIMESTAMP NULL,
                created_at TIMESTAMP NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMP NOT NULL DEFAULT NOW()
            );
            """,
            "ALTER TABLE res_users ADD COLUMN IF NOT EXISTS last_login TIMESTAMP NULL;",
            "ALTER TABLE res_users ADD COLUMN IF NOT EXISTS company_id INTEGER REFERENCES res_company(id) ON DELETE SET NULL;",
            "ALTER TABLE res_users ADD COLUMN IF NOT EXISTS employee_id INTEGER;",

            # 3. res_company columns if existed before
            "ALTER TABLE res_company ADD COLUMN IF NOT EXISTS country VARCHAR(100) DEFAULT 'India';",
            "ALTER TABLE res_company ADD COLUMN IF NOT EXISTS street VARCHAR(255);",
            "ALTER TABLE res_company ADD COLUMN IF NOT EXISTS city VARCHAR(100);",
            "ALTER TABLE res_company ADD COLUMN IF NOT EXISTS state VARCHAR(100);",
            "ALTER TABLE res_company ADD COLUMN IF NOT EXISTS zip_code VARCHAR(20);",
            "ALTER TABLE res_company ADD COLUMN IF NOT EXISTS website VARCHAR(255);",
            "ALTER TABLE res_company ADD COLUMN IF NOT EXISTS currency VARCHAR(10) DEFAULT 'INR';",
            "ALTER TABLE res_company ADD COLUMN IF NOT EXISTS color VARCHAR(20) DEFAULT '#0284c7';",

            # 4. hr_department table
            """
            CREATE TABLE IF NOT EXISTS hr_department (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL UNIQUE,
                code VARCHAR(20),
                manager_id INTEGER,
                parent_id INTEGER REFERENCES hr_department(id) ON DELETE SET NULL,
                color VARCHAR(20) NOT NULL DEFAULT '#0284c7',
                is_active BOOLEAN NOT NULL DEFAULT TRUE,
                created_at TIMESTAMP NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMP NOT NULL DEFAULT NOW()
            );
            """,

            # 5. employee table
            """
            CREATE TABLE IF NOT EXISTS employee (
                id SERIAL PRIMARY KEY,
                employee_code VARCHAR(50) NOT NULL UNIQUE,
                name VARCHAR(150) NOT NULL,
                email VARCHAR(150) NOT NULL UNIQUE,
                phone VARCHAR(20),
                department VARCHAR(100),
                job_title VARCHAR(100),
                date_joined DATE NOT NULL DEFAULT CURRENT_DATE,
                is_active BOOLEAN NOT NULL DEFAULT TRUE,
                created_at TIMESTAMP NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMP NOT NULL DEFAULT NOW()
            );
            """,

            # 6. employee additional columns
            "ALTER TABLE employee ADD COLUMN IF NOT EXISTS department_id INTEGER REFERENCES hr_department(id) ON DELETE SET NULL;",
            "ALTER TABLE employee ADD COLUMN IF NOT EXISTS gender VARCHAR(20);",
            "ALTER TABLE employee ADD COLUMN IF NOT EXISTS date_of_birth DATE;",
            "ALTER TABLE employee ADD COLUMN IF NOT EXISTS marital_status VARCHAR(20);",
            "ALTER TABLE employee ADD COLUMN IF NOT EXISTS blood_group VARCHAR(10);",
            "ALTER TABLE employee ADD COLUMN IF NOT EXISTS father_spouse_name VARCHAR(150);",
            "ALTER TABLE employee ADD COLUMN IF NOT EXISTS emergency_contact_name VARCHAR(150);",
            "ALTER TABLE employee ADD COLUMN IF NOT EXISTS emergency_contact_relation VARCHAR(50);",
            "ALTER TABLE employee ADD COLUMN IF NOT EXISTS emergency_contact_phone VARCHAR(20);",
            "ALTER TABLE employee ADD COLUMN IF NOT EXISTS pan_number VARCHAR(10);",
            "ALTER TABLE employee ADD COLUMN IF NOT EXISTS aadhaar_number VARCHAR(12);",
            "ALTER TABLE employee ADD COLUMN IF NOT EXISTS passport_number VARCHAR(20);",
            "ALTER TABLE employee ADD COLUMN IF NOT EXISTS uan_number VARCHAR(20);",
            "ALTER TABLE employee ADD COLUMN IF NOT EXISTS pf_number VARCHAR(50);",
            "ALTER TABLE employee ADD COLUMN IF NOT EXISTS esic_number VARCHAR(25);",
            "ALTER TABLE employee ADD COLUMN IF NOT EXISTS current_address TEXT;",
            "ALTER TABLE employee ADD COLUMN IF NOT EXISTS current_city VARCHAR(100);",
            "ALTER TABLE employee ADD COLUMN IF NOT EXISTS current_state VARCHAR(100);",
            "ALTER TABLE employee ADD COLUMN IF NOT EXISTS current_pincode VARCHAR(10);",
            "ALTER TABLE employee ADD COLUMN IF NOT EXISTS permanent_address TEXT;",
            "ALTER TABLE employee ADD COLUMN IF NOT EXISTS permanent_city VARCHAR(100);",
            "ALTER TABLE employee ADD COLUMN IF NOT EXISTS permanent_state VARCHAR(100);",
            "ALTER TABLE employee ADD COLUMN IF NOT EXISTS permanent_pincode VARCHAR(10);",
            "ALTER TABLE employee ADD COLUMN IF NOT EXISTS employment_type VARCHAR(50) DEFAULT 'Full-Time';",
            "ALTER TABLE employee ADD COLUMN IF NOT EXISTS branch VARCHAR(100) DEFAULT 'Pune HQ';",
            "ALTER TABLE employee ADD COLUMN IF NOT EXISTS confirmation_date DATE;",
            "ALTER TABLE employee ADD COLUMN IF NOT EXISTS avatar_url VARCHAR(255);",
            "ALTER TABLE employee ADD COLUMN IF NOT EXISTS hourly_cost NUMERIC(10,2) DEFAULT 0.00;",
            "ALTER TABLE employee ADD COLUMN IF NOT EXISTS annual_ctc NUMERIC(12,2) DEFAULT 0.00;",
            "ALTER TABLE employee ADD COLUMN IF NOT EXISTS bank_name VARCHAR(150);",
            "ALTER TABLE employee ADD COLUMN IF NOT EXISTS bank_account_number VARCHAR(50);",
            "ALTER TABLE employee ADD COLUMN IF NOT EXISTS ifsc_code VARCHAR(15);",
            "ALTER TABLE employee ADD COLUMN IF NOT EXISTS bank_branch VARCHAR(150);",
            "ALTER TABLE employee ADD COLUMN IF NOT EXISTS timesheet_approver_id INTEGER REFERENCES employee(id) ON DELETE SET NULL;",
            "ALTER TABLE employee ADD COLUMN IF NOT EXISTS leave_approver_l1_id INTEGER REFERENCES employee(id) ON DELETE SET NULL;",
            "ALTER TABLE employee ADD COLUMN IF NOT EXISTS leave_approver_l2_id INTEGER REFERENCES employee(id) ON DELETE SET NULL;",
            "ALTER TABLE employee ADD COLUMN IF NOT EXISTS expense_approver_l1_id INTEGER REFERENCES employee(id) ON DELETE SET NULL;",
            "ALTER TABLE employee ADD COLUMN IF NOT EXISTS expense_approver_l2_id INTEGER REFERENCES employee(id) ON DELETE SET NULL;",

            # 7. attendance table
            """
            CREATE TABLE IF NOT EXISTS attendance (
                id SERIAL PRIMARY KEY,
                employee_id INTEGER REFERENCES employee(id) ON DELETE RESTRICT,
                date DATE NOT NULL DEFAULT CURRENT_DATE,
                check_in TIMESTAMP NULL,
                check_out TIMESTAMP NULL,
                status VARCHAR(20) NOT NULL DEFAULT 'Present',
                input_mode_in VARCHAR(50) DEFAULT 'Biometric',
                input_mode_out VARCHAR(50) DEFAULT 'Biometric',
                is_active BOOLEAN NOT NULL DEFAULT TRUE,
                created_at TIMESTAMP NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMP NOT NULL DEFAULT NOW()
            );
            """,
            "ALTER TABLE attendance ADD COLUMN IF NOT EXISTS input_mode_in VARCHAR(50) DEFAULT 'Biometric';",
            "ALTER TABLE attendance ADD COLUMN IF NOT EXISTS input_mode_out VARCHAR(50) DEFAULT 'Biometric';",

            # 8. leave_type table
            """
            CREATE TABLE IF NOT EXISTS leave_type (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL UNIQUE,
                code VARCHAR(50),
                color VARCHAR(20) DEFAULT '#0284c7',
                max_days_per_year INTEGER NOT NULL DEFAULT 15,
                requires_allocation BOOLEAN DEFAULT FALSE,
                take_time_off_in VARCHAR(20) DEFAULT 'Day',
                approval_type VARCHAR(50) DEFAULT 'By Time Off Officer',
                is_active BOOLEAN NOT NULL DEFAULT TRUE,
                created_at TIMESTAMP NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMP NOT NULL DEFAULT NOW()
            );
            """,
            "ALTER TABLE leave_type ADD COLUMN IF NOT EXISTS code VARCHAR(50);",
            "ALTER TABLE leave_type ADD COLUMN IF NOT EXISTS color VARCHAR(20) DEFAULT '#0284c7';",
            "ALTER TABLE leave_type ADD COLUMN IF NOT EXISTS take_time_off_in VARCHAR(20) DEFAULT 'Day';",
            "ALTER TABLE leave_type ADD COLUMN IF NOT EXISTS requires_allocation BOOLEAN DEFAULT FALSE;",
            "ALTER TABLE leave_type ADD COLUMN IF NOT EXISTS approval_type VARCHAR(50) DEFAULT 'By Time Off Officer';",

            # 9. leave_request table
            """
            CREATE TABLE IF NOT EXISTS leave_request (
                id SERIAL PRIMARY KEY,
                employee_id INTEGER NOT NULL REFERENCES employee(id) ON DELETE RESTRICT,
                leave_type_id INTEGER NOT NULL REFERENCES leave_type(id) ON DELETE RESTRICT,
                start_date DATE NOT NULL,
                end_date DATE NOT NULL,
                duration_days NUMERIC(5,2) DEFAULT 1.00,
                reason TEXT,
                refusal_reason TEXT,
                status VARCHAR(20) NOT NULL DEFAULT 'Pending',
                approved_by INTEGER REFERENCES employee(id) ON DELETE RESTRICT,
                is_active BOOLEAN NOT NULL DEFAULT TRUE,
                created_at TIMESTAMP NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMP NOT NULL DEFAULT NOW()
            );
            """,
            "ALTER TABLE leave_request ADD COLUMN IF NOT EXISTS duration_days NUMERIC(5,2) DEFAULT 1.00;",
            "ALTER TABLE leave_request ADD COLUMN IF NOT EXISTS refusal_reason TEXT;",
            "ALTER TABLE leave_request DROP CONSTRAINT IF EXISTS leave_request_status_check;",
            "ALTER TABLE leave_request ADD CONSTRAINT leave_request_status_check CHECK (status IN ('draft', 'confirm', 'validate', 'refuse', 'Pending', 'Approved', 'Rejected'));",

            # 10. leave_allocation table
            """
            CREATE TABLE IF NOT EXISTS leave_allocation (
                id SERIAL PRIMARY KEY,
                name VARCHAR(150) NOT NULL,
                employee_id INTEGER REFERENCES employee(id) ON DELETE CASCADE,
                leave_type_id INTEGER REFERENCES leave_type(id) ON DELETE CASCADE,
                allocated_days NUMERIC(5,2) NOT NULL DEFAULT 0.00,
                valid_from DATE,
                valid_to DATE,
                approver_id INTEGER REFERENCES employee(id) ON DELETE SET NULL,
                status VARCHAR(20) NOT NULL DEFAULT 'Approved',
                notes TEXT,
                is_active BOOLEAN NOT NULL DEFAULT TRUE,
                created_at TIMESTAMP NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMP NOT NULL DEFAULT NOW()
            );
            """,
            "ALTER TABLE leave_allocation ADD COLUMN IF NOT EXISTS valid_from DATE;",
            "ALTER TABLE leave_allocation ADD COLUMN IF NOT EXISTS valid_to DATE;",
            "ALTER TABLE leave_allocation ADD COLUMN IF NOT EXISTS approver_id INTEGER REFERENCES employee(id) ON DELETE SET NULL;",

            # 11. leave_mandatory_day table
            """
            CREATE TABLE IF NOT EXISTS leave_mandatory_day (
                id SERIAL PRIMARY KEY,
                name VARCHAR(150) NOT NULL,
                start_date DATE NOT NULL DEFAULT CURRENT_DATE,
                end_date DATE NOT NULL DEFAULT CURRENT_DATE,
                color VARCHAR(20) NOT NULL DEFAULT '#ef4444',
                is_mandatory BOOLEAN NOT NULL DEFAULT TRUE,
                notes TEXT,
                is_active BOOLEAN NOT NULL DEFAULT TRUE,
                created_at TIMESTAMP NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMP NOT NULL DEFAULT NOW()
            );
            """,
            "ALTER TABLE leave_mandatory_day ADD COLUMN IF NOT EXISTS start_date DATE;",
            "ALTER TABLE leave_mandatory_day ADD COLUMN IF NOT EXISTS end_date DATE;",
            "ALTER TABLE leave_mandatory_day ADD COLUMN IF NOT EXISTS is_mandatory BOOLEAN DEFAULT TRUE;",
            "ALTER TABLE leave_mandatory_day ADD COLUMN IF NOT EXISTS notes TEXT;",
            "DO $$ BEGIN BEGIN ALTER TABLE leave_mandatory_day ALTER COLUMN date DROP NOT NULL; EXCEPTION WHEN OTHERS THEN NULL; END; END $$;",

            # 12. ir_sequence columns
            """
            CREATE TABLE IF NOT EXISTS ir_sequence (
                id SERIAL PRIMARY KEY,
                code VARCHAR(100) NOT NULL UNIQUE,
                name VARCHAR(150),
                prefix VARCHAR(50),
                suffix VARCHAR(100),
                padding INTEGER NOT NULL DEFAULT 4,
                next_number INTEGER NOT NULL DEFAULT 1,
                step INTEGER DEFAULT 1,
                implementation VARCHAR(20) DEFAULT 'standard',
                use_date_range BOOLEAN DEFAULT FALSE,
                company_id INTEGER REFERENCES res_company(id) ON DELETE SET NULL,
                is_active BOOLEAN NOT NULL DEFAULT TRUE,
                created_at TIMESTAMP NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMP NOT NULL DEFAULT NOW()
            );
            """,
            "ALTER TABLE ir_sequence ADD COLUMN IF NOT EXISTS name VARCHAR(150);",
            "ALTER TABLE ir_sequence ADD COLUMN IF NOT EXISTS implementation VARCHAR(20) DEFAULT 'standard';",
            "ALTER TABLE ir_sequence ADD COLUMN IF NOT EXISTS suffix VARCHAR(100);",
            "ALTER TABLE ir_sequence ADD COLUMN IF NOT EXISTS use_date_range BOOLEAN DEFAULT FALSE;",
            "ALTER TABLE ir_sequence ADD COLUMN IF NOT EXISTS step INTEGER DEFAULT 1;",
            "ALTER TABLE ir_sequence ADD COLUMN IF NOT EXISTS company_id INTEGER REFERENCES res_company(id) ON DELETE SET NULL;",

            # 13. res_groups constraint fix: drop legacy unique(name), enforce unique(privilege, name)
            "ALTER TABLE res_groups DROP CONSTRAINT IF EXISTS res_groups_name_key;",
            """
            DO $$ BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM pg_constraint WHERE conname = 'res_groups_privilege_name_key'
                ) THEN
                    ALTER TABLE res_groups ADD CONSTRAINT res_groups_privilege_name_key UNIQUE (privilege, name);
                END IF;
            END $$;
            """,
        ]

        with connection.cursor() as cursor:
            for stmt in ddl_statements:
                try:
                    cursor.execute(stmt)
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f"Note on DDL statement: {e}"))

        self.stdout.write(self.style.SUCCESS("Database schema verification and sync complete."))
