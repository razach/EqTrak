# Template Structure Documentation

[← Back to Documentation](README.md) | [Data Model](Data%20Model.md) | [Design Document](Design%20Document.md)

## Overview
The EqTrak application uses Django templates organized by app functionality, with reusable components separated into dedicated folders. This document outlines the template structure and best practices.

## Directory Structure

```
EqTrak/
├── metrics/
│   └── templates/
│       └── metrics/
│           ├── components/
│           │   └── position_metrics_card.html    # Reusable metrics display component
│           ├── position_metrics.html             # Full metrics history view
│           ├── metric_type_form.html            # Form for metric types
│           └── metric_value_form.html           # Form for editing metric values
│
└── portfolio/
    └── templates/
        └── portfolio/
            ├── components/
            │   └── transactions_card.html        # Reusable transactions display component
            ├── position_detail.html              # Position details page
            ├── portfolio_list.html               # Portfolio listing page
            ├── position_form.html                # Position creation/editing form
            ├── portfolio_detail.html             # Portfolio details page
            ├── position_confirm_delete.html      # Position deletion confirmation
            ├── transaction_form.html             # Transaction form
            └── portfolio_form.html               # Portfolio creation/editing form
```

## Component Templates
Reusable components are stored in a `components/` directory within each app's template folder. These are partial templates that can be included in multiple pages.

### Current Components:
1. `metrics/components/position_metrics_card.html`
   - Quick overview of current metric values for a position
   - Used in position detail view
   - Features:
     - Real-time computed metrics display
     - Market price with date indicators
     - Visual indicators for metric types (computed vs manual)
     - Support for memo-type metrics
     - Forecast scenario indicators
     - Confidence score display
     - Link to full metrics history

2. `metrics/components/metric_types_list.html`
   - Displays available metric types grouped by scope
   - Used in metric type management
   - Features:
     - Grouped by scope type (Position, Portfolio, Transaction)
     - System vs user-defined indicators
     - Computation status and dependencies
     - Data type indicators
     - Tag-based filtering

3. `portfolio/components/transactions_card.html`
   - Displays transactions for a position
   - Used in position detail view
   - Features: transaction list, add transaction dropdown

## Usage Guidelines

### Including Components
Components are included using Django's template include tag:
```django
{% include 'metrics/components/position_metrics_card.html' %}
{% include 'portfolio/components/transactions_card.html' %}
```

### Template Organization
1. Each app has its own templates directory
2. Reusable components go in the `components/` subdirectory
3. Main page templates are in the root of the app's template directory
4. Form templates are suffixed with `_form.html`
5. Confirmation templates are suffixed with `_confirm_delete.html`

### Best Practices
1. Keep components focused and single-purpose
2. Use consistent naming conventions
3. Document required context variables in template comments
4. Use Bootstrap classes for consistent styling
5. Format numeric values using appropriate filters (e.g., `floatformat:2` for currency)
6. Use appropriate visual indicators for data status (e.g., warning colors for outdated data)

## Context Requirements

### Position Metrics Card
Required context:
- `position_metrics`: List of metric objects with their types and values
- `portfolio`: Portfolio object
- `position`: Position object

Features:
- Displays current metric values in a compact table
- Shows computed status with calculator icon
- Indicates market price freshness with color-coded dates
- Links to full metrics history view

### Position Metrics Page
Required context:
- `metrics_by_type`: Dictionary of metric types and their values
- `portfolio`: Portfolio object
- `position`: Position object

Features:
- Full history of all metrics
- Detailed view with categories and data types
- Edit capability for non-computed metrics
- Visual indicators for computed and market price metrics

### Metric Value Form
Required context:
- `metric_type`: MetricType object
- `portfolio`: Portfolio object
- `position`: Position object
- `form`: MetricValueForm instance

Features:
- Focused form for editing single metric values
- Data type specific validation
- Optional notes field
- Visual indicators for metric type and data format

## Styling
All templates use Bootstrap 5 for styling and layout. Common components include:
- Cards with white headers and subtle shadows
- Responsive tables with hover effects
- Bootstrap Icons for visual indicators
- Utility classes for spacing and alignment
- Consistent color coding:
  - Secondary badges for computed metrics
  - Warning color for outdated market prices
  - Danger color for missing required data

## Related Documentation
- [Data Model](Data%20Model.md) - Database schema and relationships
- [Design Document](Design%20Document.md) - Application design and features

## Template Filters
The application uses custom template filters to format and display data consistently across templates.

### Portfolio Filters
Located in `portfolio/templatetags/portfolio_filters.py`:

1. `metric_display_value`
   - **Usage**: `{{ position|metric_display_value:metric_name }}`
   - **Purpose**: Formats metric values with appropriate currency symbols and decimal places
   - **Features**:
     - Adds currency symbol for monetary values
     - Adds % symbol for percentage values
     - Formats decimals consistently
     - Returns None gracefully

2. `portfolio_metric_value`
   - **Usage**: `{{ portfolio|portfolio_metric_value:metric_name }}`
   - **Purpose**: Retrieves and formats portfolio-level metric values
   - **Features**:
     - Handles system metrics
     - Returns raw value for template formatting

### Using Template Filters
1. Load the filters at the top of your template:
   ```django
   {% load portfolio_filters %}
   ```

2. Apply filters in your template:
   ```django
   {% with value=portfolio|portfolio_metric_value:"Total Value" %}
       {% if value %}
           {{ portfolio.currency }} {{ value|floatformat:2 }}
       {% else %}
           <span class="text-muted">—</span>
       {% endif %}
   {% endwith %}
   ```

### Best Practices
1. Use template filters for consistent formatting
2. Combine with built-in filters when needed (e.g., `floatformat`, `default`)
3. Handle None values gracefully
4. Use descriptive filter names
5. Document filter parameters in code 