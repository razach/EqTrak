# Test Users in EqTrak

EqTrak includes test users for development and testing purposes. These users are created using the fixture-based configuration approach rather than migrations.

## Available Test Users

| Username    | Password        | Role        | Notes                          |
|-------------|-----------------|-------------|--------------------------------|
| test_user1  | TempPass123!@#  | Staff       | Standard test user with admin  |
| test_user2  | TempPass456!@#  | Staff       | Alternative test user          |

## Creating Test Users

Test users are defined in `users/fixtures/test_users.json` and can be loaded using:

```bash
# Check if test users exist
python manage.py load_test_users --check

# Create test users in development environment
python manage.py load_test_users

# Force creating test users (even in production - USE CAUTION)
python manage.py load_test_users --force
```

## Automatic Checking

The users app automatically checks for the existence of test users during initialization in development environments. If test users are missing, a warning is logged.

## Security Notes

1. The `load_test_users` command includes a safety check to prevent accidental creation of test users in production.
2. Test user passwords are pre-hashed in the fixture file for security.
3. The command will refuse to run in production unless the `--force` flag is used.

## Customizing Test Users

To customize or add test users:

1. Edit the `users/fixtures/test_users.json` file
2. Use the following format:

```json
{
  "model": "auth.user",
  "fields": {
    "username": "my_test_user",
    "email": "testuser@example.com",
    "password": "<hashed_password>",
    "is_staff": true,
    "is_active": true
  }
}
```

To generate a hashed password for use in fixtures:

```python
from django.contrib.auth.hashers import make_password
make_password("your_password_here")
```

## Related Documentation
- [Development Guide](DEVELOPMENT.md) - Development tools and workflows
- [Design Document](Design%20Document.md) - Application design and features
- [Data Model](Data%20Model.md) - Database schema and user table details 