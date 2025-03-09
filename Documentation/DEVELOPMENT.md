# EqTrak Development Guide

This guide provides information on development practices, tools, and workflow for the EqTrak project.

## Local Development

### Requirements

- Python 3.9+
- Django 4.2.x
- SQLite (development) or PostgreSQL (production)

### Setting Up Development Environment

1. Clone the repository
2. Create a virtual environment: `python -m venv .venv`
3. Activate the environment: 
   - Windows: `.venv\Scripts\activate`
   - MacOS/Linux: `source .venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Run migrations: `python manage.py migrate`
6. Create a superuser: `python manage.py createsuperuser`
7. Start the development server: `python manage.py runserver`

## Database Management Tools

EqTrak includes scripts that help with database management during development.

### Database Reset Scripts

#### Basic Reset Script (`reset_db.sh`)

This script provides a clean slate for development by:

- Deleting the SQLite database file
- Removing all migration files (while preserving `__init__.py` files)
- Creating fresh migrations
- Applying the migrations
- Creating a new superuser

**Usage:**
```bash
# Make executable
chmod +x reset_db.sh

# Run
./reset_db.sh
```

**When to use:**
- When you've made significant model changes
- When your migrations have become complex or conflicted
- When you want to start with a clean database

#### Reset with Test Users (`reset_db_with_testusers.sh`)

This enhanced script does everything the basic script does, plus:

- Automatically creates test users (defined in `test_users.md`)
- Makes these users staff members so they can access the admin site
- Gives you the option to create a superuser or not

**Usage:**
```bash
# Make executable
chmod +x reset_db_with_testusers.sh

# Run
./reset_db_with_testusers.sh
```

**Test Users Created:**
- Username: test_user1, Password: TempPass123!@#
- Username: test_user2, Password: TempPass456!@#

**When to use:**
- For rapid development cycles where you need test users
- When testing user-specific features
- For team members who need a consistent set of users

## Working with Migrations

### Creating Migrations

After making model changes:
```bash
python manage.py makemigrations
```

### Applying Migrations

```bash
python manage.py migrate
```

### Data Migrations

EqTrak uses data migrations for:
- Creating system metrics
- Creating test users

To create a new data migration:
```bash
python manage.py makemigrations app_name --empty
```

Then edit the migration file to include the necessary operations.

## Testing

### Running Tests

```bash
# Run all tests
python manage.py test

# Run tests for a specific app
python manage.py test app_name

# Run a specific test
python manage.py test app_name.tests.TestClassName.test_method_name
```

## Code Organization

EqTrak follows a modular architecture with separate Django apps:

- `portfolio`: Core portfolio tracking functionality
- `metrics`: System-defined metrics and calculations
- `user_metrics`: User-defined metrics
- `users`: User management
- `market_data`: External market data integration

Each app has its own:
- Models
- Views
- URLs
- Templates
- Static files
- README.md with app-specific documentation

## Toggling Features

EqTrak supports toggling certain functionality on/off:

- Market data integration
- User-defined metrics

See [APP_TOGGLES.md](APP_TOGGLES.md) for more information. 