#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Convert static asset files to static root
python manage.py collectstatic --no-input

# Apply any outstanding database migrations
python manage.py migrate

# Sync dynamic model registries & seed UI views
python manage.py sync_ir_models
python manage.py seed_ir_views
