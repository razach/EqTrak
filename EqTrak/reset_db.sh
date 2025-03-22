#!/bin/bash
# Script to completely reset the database and recreate all migrations
# This is more aggressive than reset_db_with_testusers.sh and should be used
# when you need to completely rebuild the migration history

# Determine script location and set paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MANAGE_PY="${SCRIPT_DIR}/manage.py"
DB_PATH="${SCRIPT_DIR}/db.sqlite3"
PROJECT_ROOT="${SCRIPT_DIR}"

# Go to the project root directory
cd "${SCRIPT_DIR}"

echo "WARNING: This will delete your database AND ALL MIGRATIONS!"
echo "This should only be used when you need to recreate migrations from scratch."
echo "For normal development, use reset_db_with_testusers.sh instead."
read -p "Are you sure you want to continue? (y/n): " confirm

if [ "$confirm" != "y" ]; then
  echo "Operation cancelled."
  exit 0
fi

# Delete the database
echo "Deleting database..."
if [ -f "$DB_PATH" ]; then
  rm -f "$DB_PATH"
  echo "Database deleted successfully."
else
  echo "Database file not found at $DB_PATH. Creating a new one."
fi

# Delete all migrations
echo "Deleting migrations..."
find "${PROJECT_ROOT}" -path "*/migrations/*.py" -not -name "__init__.py" -delete
find "${PROJECT_ROOT}" -path "*/migrations/*.pyc" -delete

# Create fresh migrations
echo "Creating fresh migrations..."
python "$MANAGE_PY" makemigrations

# Set environment variable to prevent auto-loading metrics during app initialization
export SKIP_AUTO_METRICS_LOAD=1
echo "Setting SKIP_AUTO_METRICS_LOAD=1 to prevent duplicate metrics loading"

# Apply migrations
echo "Applying migrations..."
python "$MANAGE_PY" migrate

# Initialize app settings to ensure they're enabled by default
echo "Initializing app settings..."
python "$MANAGE_PY" init_app_settings

# Clear any metrics that might have been created by migrations
echo "Clearing existing metrics before loading fixtures..."
python "$MANAGE_PY" clear_metrics --confirm

# Create a superuser
echo "Creating superuser..."
python "$MANAGE_PY" createsuperuser

# Load all metrics using the configure_metrics command with --sync flag
echo "Loading metrics fixtures..."
python "$MANAGE_PY" configure_metrics --load --sync
echo "All metrics loaded successfully with sync option to prevent duplicates."

# Load test users from fixtures
echo "Creating test users..."
python "$MANAGE_PY" load_test_users
echo "Test users created successfully."

echo "Full database reset completed successfully!"
echo "You may now run the server with: python $MANAGE_PY runserver" 