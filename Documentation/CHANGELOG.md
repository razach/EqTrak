# EqTrak Changelog

## Version 0.2.0 - Performance Module Fixes - 2023-03

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

## Version 0.1.0 - Initial Release - 2023-02

- Basic portfolio tracking functionality
- Position and transaction management
- Market data integration
- Performance metrics
- Custom user-defined metrics 