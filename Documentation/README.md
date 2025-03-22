# EqTrak Documentation

Welcome to the EqTrak documentation. This resource contains information about the application's architecture, features, and development guidelines.

## Core Documentation

- [Architecture](Architecture.md): System architecture and design principles
- [Data Model](Data%20Model.md): Database schema and relationships
- [Design Document](Design%20Document.md): Overall design philosophy and decisions
- [Development Guide](DEVELOPMENT.md): Development workflow and tools
- [Development Setup](DEVELOPMENT_SETUP.md): Setting up the development environment
- [Changelog](CHANGELOG.md): History of changes and recent fixes

## Feature Documentation

- [Performance Module](PERFORMANCE_MODULE.md): Performance tracking and calculations
- [App Toggles](APP_TOGGLES.md): Feature flag system
- [Market Data Controls](Market%20Data%20Controls.md): Market data integration
- [Templates](templates.md): Template structure and usage

## Development Practices

- [Fixture-Based Configuration](fixture_based_configuration.md): Our approach to application configuration
- [Test Users](test_users.md): Test user management for development

## Project Management

- [TODO](TODO.md): Current development tasks and roadmap

## Recent Improvements

The latest version (0.2.0) includes important fixes to the Performance module:

- Fixed UUID handling in performance metrics using `CharField` instead of integer field
- Corrected primary key references in calculation services
- Improved template handling for performance metrics display
- Enhanced error handling and troubleshooting

For complete details of recent changes, see the [Changelog](CHANGELOG.md).

## Key Development Approaches

### Fixture-Based Configuration

EqTrak uses a fixture-based approach for application configuration:

- **Schema in Migrations**: Only structural database changes in migrations
- **Data in Fixtures**: Configuration data stored in JSON fixtures
- **Automatic Loading**: Configuration loaded at application startup

For more information, see [Fixture-Based Configuration](fixture_based_configuration.md).

### Module Separation

Features are organized into separate Django apps for:

- Clean separation of concerns
- Ability to enable/disable features
- Independent development and testing

See [Architecture](Architecture.md) for details on our modular approach.

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
- **Performance**: Gain/loss calculations and tracking

## Module-Specific Documentation

Each module has its own README file with detailed information:

- [Metrics Module](../EqTrak/metrics/README.md) - Core metrics functionality
- [User Metrics Module](../EqTrak/user_metrics/README.md) - User-defined metrics functionality
- [Performance Module](../EqTrak/performance/README.md) - Performance tracking and calculations

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

## Troubleshooting

Common issues and solutions are documented in the [Development Setup](DEVELOPMENT_SETUP.md#troubleshooting) guide.

## Test Users

See [test_users.md](test_users.md) for test user credentials and related information.

## TODO List

See [TODO.md](TODO.md) for a list of planned features and improvements.