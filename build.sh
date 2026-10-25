#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Ensure database schema compatibility before migrations
python manage.py ensure_db_schema

# Apply any outstanding database migrations
python manage.py migrate --fake-initial || python manage.py migrate

# Shared cache table used by login / OTP brute-force throttling (safe to re-run)
python manage.py createcachetable

# Convert static asset files to static root
python manage.py collectstatic --no-input

# Sync dynamic model registries & seed UI views, actions, sequences, cron, and leave data
python manage.py sync_ir_models
python manage.py seed_technical_defaults
python manage.py seed_ir_views
python manage.py seed_leave_data

# Security: hash any plaintext passwords, keep legacy admins as explicit admins, report weak passwords
python manage.py harden_accounts

# Assign department managers and reporting hierarchies
python manage.py assign_department_managers
