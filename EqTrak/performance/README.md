# Performance Module

The Performance module provides gain/loss calculation functionality for EqTrak.

## Development Approach

This module uses a fixture-based approach to configure metrics:
- All metrics are defined in `fixtures/performance_metrics.json` 
- Metrics are automatically loaded at application startup
- No data migrations are used for configuration

Since this app is still in development, we prioritize simplicity over migration history:
- Only schema changes are included in migrations
- Configuration data comes from fixtures
- The `AppConfig.ready()` method ensures metrics are loaded at startup

## Features

- Calculates position and portfolio gain/loss metrics
- Provides both absolute and percentage-based calculations
- Integrates with the metrics system for display
- Supports per-user enabling/disabling of performance tracking
- System-wide performance tracking control

## Architecture

The Performance module is designed to be cleanly separable from the core EqTrak functionality:

1. **Service Layer**: All gain/loss calculations are centralized in `services.py`
2. **Metrics Integration**: `metrics.py` handles updating the metrics system
3. **Patches**: `patches.py` provides runtime patches to prevent metrics from displaying when disabled
4. **Models**: Minimal models used only for configuration

## Implementation Notes

### UUID Support
The performance module uses Django's ContentTypes framework to store generic foreign keys to portfolios, positions, and transactions. Important implementation points:

- **Generic Foreign Keys**: The `PerformanceMetric` model uses Content Types to reference different objects
- **UUID Storage**: The `object_id` field is a `CharField(max_length=40)` to store UUIDs as strings
- **Primary Key References**: Always use model-specific primary key fields:
  - `portfolio.portfolio_id` 
  - `position.position_id`
  - `transaction.transaction_id`

### Metrics Integration
The performance module integrates with the metrics system through:

- Runtime patching of `MetricType.get_system_metric` to respect feature toggle
- Custom template tags to control display of metrics
- Custom filters to format gain/loss values

### Template Usage Best Practices
When using performance template tags in templates:

```django
{# Store the result of the tag in a variable first #}
{% can_access_performance_metrics as can_access %}

{# Then use the variable in conditionals #}
{% if can_access %}
    {# Performance features are accessible #}
{% endif %}
```

## Installation

The Performance module is included with EqTrak by default. During development:

1. Include 'performance' in INSTALLED_APPS in settings.py
2. Run migrations: `python manage.py migrate performance`
3. Metrics are automatically loaded at application startup

## Configuration

### System-wide Settings

System-wide performance tracking can be controlled via the admin interface:

1. Navigate to Admin > Performance > Performance Settings
2. Check/uncheck "Updates Enabled" to enable/disable performance tracking system-wide

### User Settings

Individual users can enable/disable performance tracking in their user settings:

1. Navigate to User Settings
2. Check/uncheck "Enable Performance Tracking"

## Managing Performance Metrics

You can use management commands to directly control metrics:

```bash
# Show the current status of metrics
python manage.py toggle_performance_metrics --status

# Activate performance metrics
python manage.py toggle_performance_metrics --activate

# Deactivate performance metrics
python manage.py toggle_performance_metrics --deactivate

# Load and update metrics from fixtures
python manage.py configure_metrics --load --module=performance
```

## Disabling the Module

To disable the module without removing it:

```bash
python manage.py disable_performance
```

This will:
1. Disable system-wide performance tracking
2. Disable performance tracking for all users
3. Deactivate all performance-related metric types

To also clear existing performance metric values:

```bash
python manage.py disable_performance --clear-data
```

## Complete Removal

To completely remove the Performance module:

1. Run `python manage.py disable_performance --clear-data`
2. Remove 'performance' from INSTALLED_APPS in settings.py
3. Remove any references to the performance module in templates or views
4. Remove the performance directory

## Integration Points

The Performance module integrates with:

- Metrics module: Provides gain/loss values for the metrics system
- Users module: Respects user preferences for performance tracking

## Data Model

```
PerformanceSettings
  - updates_enabled: Boolean
```

## Components and Views

The module provides reusable components for UI integration:
- `position_performance_card.html`: Card component for position details
- `portfolio_performance_card.html`: Card component for portfolio details

### Views
- `/performance/`: Main performance dashboard
- `/performance/portfolio/<uuid:portfolio_id>/`: Portfolio performance view
- `/performance/portfolio/<uuid:portfolio_id>/position/<uuid:position_id>/`: Position performance view

## Overview
The Performance Module provides gain/loss calculations and tracking at the portfolio, position, and transaction levels. It allows users to track investment performance and understand their returns over time.

## Models
- **PerformanceSettings**: System-wide settings for controlling the feature
- **PerformanceMetric**: Stores calculated performance metrics for different objects

## Integration
The performance module integrates with the existing metrics module:
1. It builds upon the existing `position_gain` calculations
2. Provides more detailed tracking and separate gain/loss storage
3. Uses Django signals to update metrics when positions, portfolios, or transactions change

## Usage

### Template Tags
```
{% load performance_tags %}

{# Check if feature is enabled #}
{% is_performance_enabled as feature_enabled %}
{% if feature_enabled %}
    {# Functionality is available #}
{% endif %}

{# Get performance for a position #}
{% calculate_position_performance position user as performance %}
{% if performance %}
    Cost Basis: {{ performance.cost_basis }}
    Current Value: {{ performance.current_value }}
    Gain/Loss: {{ performance.absolute_gain_loss }}
    Return: {{ performance.percentage_gain_loss }}%
{% endif %}

{# Format gain/loss with appropriate styling #}
{% format_gain_loss value include_percent=True %}
```

### Components
The module provides reusable components for UI integration:
- `position_performance_card.html`: Card component for position details
- `portfolio_performance_card.html`: Card component for portfolio details
- `transaction_performance_card.html`: Card component for transaction details

### Views
- `/performance/`: Main performance dashboard
- `/performance/portfolio/<uuid:portfolio_id>/`: Portfolio performance view
- `/performance/portfolio/<uuid:portfolio_id>/position/<uuid:position_id>/`: Position performance view
- `/performance/portfolio/<uuid:portfolio_id>/position/<uuid:position_id>/transaction/<uuid:transaction_id>/`: Transaction performance view
- `/performance/recalculate/`: Recalculate all performance metrics

## Settings
To enable/disable the performance module:
- System-wide: Use the Django admin interface to modify PerformanceSettings
- User-specific: Each user can toggle the feature in their settings 