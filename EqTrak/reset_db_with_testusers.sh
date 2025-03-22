#!/bin/bash
# Script to reset the database with test users and configuration fixtures

# Determine script location and set paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MANAGE_PY="${SCRIPT_DIR}/manage.py"
DB_PATH="${SCRIPT_DIR}/db.sqlite3"

# Go to the project root directory
cd "${SCRIPT_DIR}"

echo "WARNING: This will delete your database!"
echo "This should only be used in development environments."
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

# Load all metrics using the configure_metrics command with --sync flag
echo "Loading metrics fixtures..."
python "$MANAGE_PY" configure_metrics --load --sync
echo "All metrics loaded successfully with sync option to prevent duplicates."

# Load test users from fixtures
echo "Creating test users..."
python "$MANAGE_PY" load_test_users
echo "Test users created successfully:"
echo "- Username: test_user1, Password: TempPass123!@#"
echo "- Username: test_user2, Password: TempPass456!@#"

# Ask if user wants to create a superuser
read -p "Do you want to create a superuser? (y/n): " create_superuser

if [ "$create_superuser" = "y" ]; then
  echo "Creating superuser..."
  python "$MANAGE_PY" createsuperuser
fi

echo "Database reset completed successfully!"
echo "You may now run the server with: python $MANAGE_PY runserver" 