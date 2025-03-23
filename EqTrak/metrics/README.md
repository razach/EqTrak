# Metrics App

This Django app provides core metrics functionality for the EqTrak system.

## Core Features

- System-defined metrics for portfolios, positions, and transactions
- Automatic metric calculations
- Historical metric values and tracking
- Metric visualization and reporting

## Integration with User-Defined Metrics

The `metrics` app provides the core metrics infrastructure, while the `user_metrics` app extends this functionality to allow users to create and manage their own custom metrics.

### Separation of Concerns

- **metrics app**: Core infrastructure, system metrics, data storage, calculation engine
- **user_metrics app**: User interface for creating/managing custom metrics, custom formula validation

### App Toggling

The `user_metrics` app can be toggled on/off in settings.py without affecting core metrics functionality:

1. To disable user-defined metrics, remove `'user_metrics'` from INSTALLED_APPS in settings.py
2. When disabled, all user interface elements for creating custom metrics will be hidden
3. Core metrics functionality will continue to work normally

## Development Notes

When adding new metric capabilities:

1. Core metric functionality should be added to the `metrics` app
2. User-facing custom metric functionality should be added to the `user_metrics` app
3. Use the `user_metrics_enabled` context variable to conditionally show UI elements

# Metrics Module

The Metrics module provides a flexible system for tracking and displaying various metrics throughout EqTrak.

## New Configuration Approach

Instead of using migrations to create and configure metrics, we now use a fixture-based approach combined with management commands. This has several advantages:

1. **Cleaner Migrations**: Migrations focus solely on database schema changes, not data configuration
2. **Easier Administration**: Metrics can be configured using simple commands instead of writing migrations
3. **More Flexibility**: Metrics can be added, modified, or deactivated without creating new migrations

## Fixture Files

Metrics are defined in JSON fixture files:

- `metrics/fixtures/standard_metrics.json` - Core metrics used by the base system
- `[module]/fixtures/[module]_metrics.json` - Module-specific metrics (e.g., performance_metrics.json)

## Management Commands

The `configure_metrics` command provides a comprehensive way to manage metrics:

```bash
# List all registered metrics
python manage.py configure_metrics --list

# Load all metrics from fixture files
python manage.py configure_metrics --load

# Load and update specific module metrics 
python manage.py configure_metrics --load --module=performance --sync

# Activate specific metrics by key
python manage.py configure_metrics --activate position_gain portfolio_return

# Deactivate specific metrics by key
python manage.py configure_metrics --deactivate position_gain portfolio_return
```

## Module Integration

Modules can integrate with metrics in two ways:

1. **Fixture Files**: By placing a `[module]_metrics.json` file in their fixtures directory
2. **AppConfig**: By calling `configure_metrics` in their `ready()` method

Example AppConfig implementation:

```python
def ready(self):
    # Ensure metrics are registered
    from django.core.management import call_command
    call_command('configure_metrics', module='my_module', sync=True)
```

## Defining New Metrics

To define new metrics, create or update a fixture file with an entry like:

```json
{
  "model": "metrics.metrictype",
  "fields": {
    "name": "My New Metric",
    "scope_type": "POSITION",
    "data_type": "PERCENTAGE",
    "computation_source": "my_source",
    "description": "Description of the metric",
    "is_system": true,
    "computation_order": 20,
    "key": "my_unique_metric_key",
    "is_active": true,
    "tags": "category1,category2,category3"
  }
}
```

## Disabling Modules That Use Metrics

When disabling a module that defines metrics, you should:

1. Deactivate the metrics: `python manage.py configure_metrics --deactivate metric_key1 metric_key2`
2. Use the module's disable command if available (e.g., `disable_performance`)

This approach ensures that metrics are properly deactivated without losing historical data 