#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Ensure database schema compatibility before migrations
python manage.py ensure_db_schema

# Apply any outstanding database migrations
python manage.py migrate --fake-initial || python manage.py migrate

# Convert static asset files to static root
python manage.py collectstatic --no-input

# Sync dynamic model registries & seed UI views
python manage.py sync_ir_models
python manage.py seed_ir_views
