# EqTrak Documentation

Welcome to the EqTrak documentation. This document provides an overview of the project structure, features, and development guidelines.

## Table of Contents

- [Architecture](#architecture)
- [Design](#design)
- [Data Model](#data-model)
- [Application Modules](#application-modules)
- [Templates](#templates)
- [App Toggles](#app-toggles)
- [Development Tools](#development-tools)
- [Test Users](#test-users)
- [TODO List](#todo-list)

## Architecture

See [Architecture.md](Architecture.md) for a detailed description of the application architecture.

## Design

See [Design Document.md](Design%20Document.md) for information about the application design, features, and user interface.

## Data Model

See [Data Model.md](Data%20Model.md) for details about the database schema, models, and relationships.

## Application Modules

EqTrak is built with a modular architecture, where functionality is separated into distinct Django apps:

### Core Modules

- **Portfolio**: Core portfolio tracking functionality
- **Metrics**: System-defined metrics and calculations
- **Users**: User management and settings

### Extension Modules

- **User Metrics**: User-defined custom metrics
- **Market Data**: External market data integration

## Module-Specific Documentation

Each module has its own README file with detailed information:

- [Metrics Module](../EqTrak/metrics/README.md) - Core metrics functionality
- [User Metrics Module](../EqTrak/user_metrics/README.md) - User-defined metrics functionality

## Templates

See [templates.md](templates.md) for information about template structure and organization.

## App Toggles

EqTrak supports toggling specific functionality on and off. See [APP_TOGGLES.md](APP_TOGGLES.md) for details on configuring toggleable features.

## Market Data Controls

Information about controlling market data integration can be found in [Market Data Controls.md](Market%20Data%20Controls.md).

## Development Tools

### Database Reset Scripts

EqTrak includes scripts to help with development database management:

#### Basic Database Reset (`reset_db.sh`)

This script resets the database to a clean state:
- Deletes the SQLite database file
- Removes all migration files (keeping `__init__.py`)
- Creates fresh migrations
- Applies migrations
- Creates a superuser

Usage:
```bash
# Make the script executable
chmod +x reset_db.sh

# Run the script
./reset_db.sh
```

#### Reset with Test Users (`reset_db_with_testusers.sh`)

This script resets the database and automatically creates test users:
- Performs all the actions of the basic reset
- Creates test users defined in [test_users.md](test_users.md)
- Gives you the option to create a superuser

Usage:
```bash
# Make the script executable
chmod +x reset_db_with_testusers.sh

# Run the script
./reset_db_with_testusers.sh
```

Test users created:
- Username: test_user1, Password: TempPass123!@#
- Username: test_user2, Password: TempPass456!@#

## Test Users

See [test_users.md](test_users.md) for test user credentials and related information.

## TODO List

See [TODO.md](TODO.md) for a list of planned features and improvements.