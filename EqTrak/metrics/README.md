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