# User Defined Metrics

This Django app provides functionality for users to define and track custom metrics in the EqTrak system.

## Features

- Create custom user-defined metrics
- Manually track metric values at portfolio, position, or transaction level
- View metric history and trends

## Usage

1. Navigate to "My Custom Metrics" in the main navigation
2. Click "Create New Custom Metric" to define a new metric
3. Provide a name, description, and select the appropriate metric type
4. Save your custom metric
5. Add values to your metrics from portfolio, position, or transaction pages

## Key Points

- User-defined metrics are manually tracked values only
- System-calculated metrics are defined and managed separately in the core metrics system
- User metrics can be created for portfolios, positions, or transactions

## Integration with Core Metrics

User-defined metrics are displayed alongside system metrics in the interface, but they:
- Cannot perform automatic calculations
- Must be updated manually by the user
- Can be enabled/disabled via the module system

## Developer Notes

The user_metrics app separates user-defined metrics from system metrics to:
- Provide a cleaner user experience
- Allow easier management of user-created content
- Enable the module to be toggled on/off

### Design Decisions

- All automatic/computed metrics are handled by the core metrics system
- User metrics are strictly manually-entered values
- The user interface makes it easy to manage both types of metrics 