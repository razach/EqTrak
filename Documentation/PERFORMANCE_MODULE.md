# Performance Module

The Performance Module provides gain/loss calculations and tracking at the portfolio, position, and transaction levels. It allows users to track investment performance and understand their returns over time.

## Overview

The Performance Module is implemented as a standalone Django app with toggle functionality, allowing users and administrators to enable or disable performance tracking as needed.

### Key Features

- Calculate gain/loss metrics at three levels: portfolio, position, and transaction
- Toggle functionality to enable/disable at both system and user levels
- Display performance metrics within the UI where appropriate
- Integration with the existing metrics system

## Implementation

### Data Models

#### PerformanceSettings
```python
class PerformanceSettings(models.Model):
    """
    Stores system-wide settings for performance calculations
    """
    updates_enabled = models.BooleanField(
        default=True,
        help_text="Enable or disable performance calculations globally"
    )
    last_modified = models.DateTimeField(auto_now=True)
```

#### PerformanceMetric
```python
class PerformanceMetric(models.Model):
    """
    Stores performance calculations at different levels
    """
    # Link to related objects - use generic foreign key
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.CharField(max_length=40)  # Support for UUID primary keys
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Performance calculations
    cost_basis = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    current_value = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    absolute_gain_loss = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    percentage_gain_loss = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Metadata
    calculation_date = models.DateTimeField(auto_now=True)
    is_realized = models.BooleanField(default=False)
```

### Key Implementation Details

#### UUID Support
The performance module uses Django's ContentTypes framework to store generic foreign keys to portfolios, positions, and transactions:

- **Generic Foreign Keys**: The `PerformanceMetric` model uses Content Types to reference different objects
- **UUID Storage**: The `object_id` field is a `CharField(max_length=40)` to store UUIDs as strings
- **Primary Key References**: Always use model-specific primary key fields:
  - `portfolio.portfolio_id` 
  - `position.position_id`
  - `transaction.transaction_id`

#### Metrics Integration
The performance module integrates with the metrics system through:

- Runtime patching of `MetricType.get_system_metric` to respect feature toggle
- Custom template tags to control display of metrics
- Custom filters to format gain/loss values

#### Template Usage
When using performance template tags in templates:

```django
{# Store the result of the tag in a variable first #}
{% can_access_performance_metrics as can_access %}

{# Then use the variable in conditionals #}
{% if can_access %}
    {# Performance features are accessible #}
{% endif %}
```

### Service Layer

The service layer handles calculation of performance metrics and integration with the metrics module:

```python
class PerformanceService:
    """Service for calculating performance metrics"""
    
    @staticmethod
    @check_performance_access
    def calculate_position_performance(position, user=None):
        """Calculate performance metrics for a position"""
        # Get or create performance metric for this position
        content_type = ContentType.objects.get_for_model(position)
        metric, created = PerformanceMetric.objects.get_or_create(
            content_type=content_type,
            object_id=position.position_id  # Use correct primary key field
        )
        
        # Calculate gains/losses...
        
        # Update metrics module
        update_position_gain_loss(position, percentage_gain_loss)
        
        return metric
```

## Recent Fixes (v0.2.0)

### Database Model Changes
- Changed `PerformanceMetric.object_id` from `PositiveIntegerField` to `CharField(max_length=40)` to properly handle UUID primary keys
- This fixes the "Python int too large to convert to SQLite INTEGER" error when creating portfolios

### Service Layer Fixes
- Fixed primary key references in performance calculation services
- Updated references from `.id` to the proper model-specific primary key fields:
  - `portfolio.portfolio_id` instead of `portfolio.id`
  - `position.position_id` instead of `position.id`
  - `transaction.transaction_id` instead of `transaction.id`
- This fixes the `AttributeError: Portfolio object has no attribute 'id'` error

### Patching Mechanism
- Refactored the patch mechanism for `MetricType.get_system_metric` to properly handle class method arguments
- Reimplemented the method directly rather than trying to call the original method with additional arguments
- Fixed the `TypeError: get_system_metric() takes from 2 to 3 positional arguments but 4 were given` error

### Template Improvements
- Fixed template conditional logic in metric_types_list.html to properly evaluate the `can_access_performance_metrics` template tag
- Added `{% can_access_performance_metrics as can_access %}` to store the result in a variable first
- Updated conditionals to use the stored variable instead of calling the tag directly
- This ensures gain/loss metrics are properly displayed when the performance module is enabled

## Configuration

### System-wide Settings

System-wide performance tracking can be controlled via the admin interface:

1. Navigate to Admin > Performance > Performance Settings
2. Check/uncheck "Updates Enabled" to enable/disable performance tracking system-wide

### User Settings

Individual users can enable/disable performance tracking in their user settings:

1. Navigate to User Settings
2. Check/uncheck "Enable Performance Tracking"

## Management Commands

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

## Provider System

The Performance Module uses a provider system to integrate with the metrics module, allowing for clean separation of concerns:

### Provider Architecture

```
metrics/                  # Metrics app
├── providers.py         # Provider registry system
│
performance/              # Performance app
├── providers.py         # Performance-specific providers
├── apps.py              # Registers providers on startup
└── integration.py       # Integration functions and constants
```

#### Metrics Provider Registry

The metrics app implements a simple provider registry that allows other apps to register calculation functions:

```python
# metrics/providers.py
METRIC_PROVIDERS = {}  # Dictionary mapping metric names to provider functions

def register_provider(metric_name, provider_function):
    """Register a function that can compute values for a specific metric"""
    global METRIC_PROVIDERS
    METRIC_PROVIDERS[metric_name] = provider_function
    
def compute_metric_value(metric_name, target_object):
    """Compute a metric value using the registered provider"""
    provider = get_provider(metric_name)
    if provider:
        return provider(target_object)
    return None
```

#### Performance Provider Registration

The performance app registers its calculation functions during app initialization:

```python
# performance/providers.py
def register_providers():
    """Register all performance metric providers with the metrics system"""
    from metrics.providers import register_provider
    
    # Register position gain/loss providers
    register_provider(POSITION_GAIN, PerformanceCalculationService.get_position_gain_percentage)
    register_provider(POSITION_GAIN_ABSOLUTE, PerformanceCalculationService.get_position_gain_absolute)
    
    # Register portfolio return providers
    register_provider(PORTFOLIO_RETURN, PerformanceCalculationService.get_portfolio_return_percentage)
    register_provider(PORTFOLIO_RETURN_ABSOLUTE, PerformanceCalculationService.get_portfolio_return_absolute)
    register_provider(PORTFOLIO_TWR, PerformanceCalculationService.get_time_weighted_return_percentage)
```

#### App Initialization

Providers are registered when the app starts:

```python
# performance/apps.py
class PerformanceConfig(AppConfig):
    # ...
    
    def ready(self):
        """Initialize the app when Django starts"""
        # Import and register performance metric providers
        from .providers import register_providers
        register_providers()
        # ...
```

### Benefits of Provider System

1. **Clean Separation of Concerns**:
   - The metrics app is agnostic about how metric values are calculated
   - The performance app contains all performance-specific calculation logic
   - No circular dependencies between the apps

2. **Extensibility**:
   - Other apps can register their own metric providers using the same mechanism
   - The metrics app doesn't need to be modified when new metric types are added

3. **Simplified Metrics Model**:
   - The metrics app's `MetricType.compute_value` method first checks for registered providers
   - Falls back to internal computation only when no provider is registered
   - Avoids complex conditional logic in the metrics app 

### Integration Functions

The performance app uses an integration module to cleanly separate calculation logic from metrics storage:

```python
# performance/integration.py
def store_position_gain_percentage(position, value):
    """Store position gain/loss percentage in the metrics system"""
    # ...

def store_position_gain_absolute(position, value):
    """Store position gain/loss absolute value in the metrics system"""
    # ...
```

These integration functions are called by the performance services after calculations are complete, providing a clean interface between the performance and metrics systems.

## Troubleshooting

See the [Development Setup](DEVELOPMENT_SETUP.md#troubleshooting) guide for common issues and solutions related to the performance module. 