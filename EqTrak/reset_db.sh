#!/bin/bash
# Script to reset the database and create fresh migrations

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

# Delete all migrations
echo "Deleting migrations..."
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/*.pyc" -delete

# Create fresh migrations
echo "Creating fresh migrations..."
python manage.py makemigrations

# Apply migrations
echo "Applying migrations..."
python manage.py migrate

# Create a superuser
echo "Creating superuser..."
python manage.py createsuperuser

echo "Database reset completed successfully!"
echo "You may now run the server with: python manage.py runserver" 