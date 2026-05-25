#!/usr/bin/env bash
# exit on error
set -o errexit

echo "Installing project dependencies..."
pip install -r requirements.txt

echo "Compiling static assets..."
python manage.py collectstatic --no-input

echo "Running migrations..."
python manage.py migrate

echo "Seeding database with default categories, tags, and users..."
python seed_data.py

echo "Build process completed successfully!"
