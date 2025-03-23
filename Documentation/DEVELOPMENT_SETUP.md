# Development Setup Guide

This guide covers setting up EqTrak for development, including the fixture-based configuration approach.

## Initial Setup

1. Clone the repository
2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Create a fresh database:
   ```bash
   python manage.py migrate
   ```

## Loading Configuration Data

The application automatically loads configuration data at startup, but you can also load it manually:

```bash
# Load all metrics configuration
python manage.py configure_metrics --load

# Load test users (for development only)
python manage.py load_test_users
```

## Fixture-Based Configuration

EqTrak uses a fixture-based approach for configuration data:

1. **Schema Changes**: Only structural database changes are in migrations
2. **Configuration Data**: Stored in JSON fixtures in each app's `fixtures/` directory
3. **Automatic Loading**: Configuration is loaded when the app starts

This approach keeps migrations clean and makes configuration changes easier to manage.

## Development Workflow

1. Run the development server:
   ```bash
   python manage.py runserver
   ```

2. Access the application at http://127.0.0.1:8000/

3. When making changes to configuration:
   - Edit the appropriate fixture file in the app's `fixtures/` directory
   - Restart the server or run the corresponding configuration command

## Testing

Run the test suite:
```bash
python manage.py test
```

## Resetting the Database

EqTrak includes scripts to help with development database management:

### Standard Development Reset

For typical development work, use:

```bash
# Make the script executable (first time only)
chmod +x EqTrak/reset_db_with_testusers.sh

# Run the script
./EqTrak/reset_db_with_testusers.sh
```

This script:
- Deletes the SQLite database
- Runs migrations
- Loads configuration from fixtures
- Creates test users
- Offers to create a superuser

### Complete Migration Reset

When you need to completely rebuild migrations:

```bash
# Make the script executable (first time only)
chmod +x EqTrak/reset_db.sh

# Run the script
./EqTrak/reset_db.sh
```

This script:
- Deletes the SQLite database
- Deletes all migration files (keeping `__init__.py`)
- Creates fresh migrations
- Applies migrations
- Creates a superuser
- Loads configuration from fixtures
- Creates test users

**Warning**: Only use this when you need to recreate migrations from scratch.

## Common Management Commands

- `python manage.py configure_metrics --list`: View all registered metrics
- `python manage.py toggle_performance_metrics --status`: Check performance metrics status
- `python manage.py disable_performance`: Disable performance module
- `python manage.py load_test_users --check`: Check if test users exist 

## Troubleshooting

### Database Errors

#### "Python int too large to convert to SQLite INTEGER"
This can occur when using UUID primary keys with SQLite and generic foreign keys:

- **Cause**: A UUID is being stored in a numeric field
- **Solution**: Check that `PerformanceMetric.object_id` is a `CharField(max_length=40)` rather than an integer field
- **Fix**: Run `./EqTrak/reset_db_with_testusers.sh` to rebuild database with the correct schema

#### "AttributeError: Object has no attribute 'id'"
Models use custom primary key names:

- **Cause**: Code is accessing `.id` instead of the correct primary key field
- **Solution**: Use model-specific primary key fields:
  - `portfolio.portfolio_id`
  - `position.position_id`
  - `transaction.transaction_id`

### Template Issues

#### Performance metrics not displaying correctly
- **Cause**: Template tags need to be evaluated and stored in variables first
- **Solution**: Use `{% can_access_performance_metrics as can_access %}` and then reference the stored variable
- **Check**: Ensure the performance module is enabled in both system and user settings

#### Method argument errors
- **Cause**: Patched classmethods can sometimes receive extra arguments
- **Solution**: Ensure patched methods handle variable arguments using `*args, **kwargs`

See the [CHANGELOG.md](./CHANGELOG.md) for details on recent fixes. 