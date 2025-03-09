#!/bin/bash
# Script to reset the database with test users

echo "WARNING: This will delete your database and all migrations!"
echo "This should only be used in development environments."
read -p "Are you sure you want to continue? (y/n): " confirm

if [ "$confirm" != "y" ]; then
  echo "Operation cancelled."
  exit 0
fi

# Delete the database
echo "Deleting database..."
rm -f db.sqlite3

# Create fresh migrations (but keep existing ones)
echo "Creating fresh migrations if needed..."
python manage.py makemigrations

# Apply migrations
echo "Applying migrations..."
python manage.py migrate

echo "Test users created:"
echo "- Username: test_user1, Password: TempPass123!@#"
echo "- Username: test_user2, Password: TempPass456!@#"

# Ask if user wants to create a superuser
read -p "Do you want to create a superuser? (y/n): " create_superuser

if [ "$create_superuser" = "y" ]; then
  echo "Creating superuser..."
  python manage.py createsuperuser
fi

echo "Database reset completed successfully!"
echo "You may now run the server with: python manage.py runserver" 