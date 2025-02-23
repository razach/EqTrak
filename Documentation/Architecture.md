# Project Architecture

[← Back to Documentation](README.md) | [Data Model](Data%20Model.md) | [Design Document](Design%20Document.md)

## Project Structure

```
EqTrak/
├── EqTrak/                  # Project configuration
│   ├── settings.py         # Project settings
│   ├── urls.py            # Root URL configuration
│   └── wsgi.py            # WSGI configuration
│
├── portfolio/              # Portfolio management app
│   ├── models.py          # Portfolio, Position, Transaction models
│   ├── views.py           # Portfolio-related views
│   ├── urls.py            # Portfolio URL patterns
│   ├── forms.py           # Portfolio-related forms
│   ├── templatetags/      # Custom template filters
│   │   └── portfolio_filters.py  # Portfolio-specific filters
│   └── templates/
│       └── portfolio/     # Portfolio templates
│           ├── components/
│           │   └── transactions_card.html
│           ├── portfolio_list.html
│           ├── portfolio_detail.html
│           └── position_detail.html
│
├── metrics/               # Metrics tracking app
│   ├── models.py         # MetricType, MetricValue models
│   ├── views.py          # Metric-related views
│   ├── urls.py           # Metrics URL patterns
│   ├── forms.py          # Metric-related forms
│   ├── context_processors.py  # Global metric context
│   ├── templatetags/    # Custom template filters
│   └── templates/
│       └── metrics/      # Metrics templates
│           ├── components/
│           │   ├── position_metrics_card.html
│           │   └── metric_types_list.html
│           ├── metric_type_form.html
│           └── metric_value_form.html
│
├── users/                # User management app
│   ├── models.py        # User profile models
│   ├── views.py         # Authentication views
│   └── urls.py          # User URL patterns
│
├── static/              # Static files
│   ├── css/
│   ├── js/
│   └── img/
│
├── templates/           # Global templates
│   ├── base.html       # Base template
│   └── home.html       # Landing page
│
└── manage.py           # Django management script
```

## App Interactions

### Portfolio App
- **Primary Purpose**: Manages portfolios, positions, and transactions
- **Dependencies**: 
  - Metrics app for position metrics
  - Users app for authentication
- **Key Features**:
  - Portfolio CRUD operations
  - Position management
  - Transaction tracking

### Metrics App
- **Primary Purpose**: Handles metric types and values
- **Dependencies**:
  - Portfolio app for position, portfolio, and transaction data
- **Key Features**:
  - Metric type definitions (system and user-defined)
  - Metric value tracking with support for:
    - Numeric and memo-type values
    - Computed metrics with dependencies
    - Forecasting with scenarios
    - Confidence scoring
  - Automated computation system
  - Validation framework
- **Global Context**:
  - Provides metric types to all templates via context processor
  - Groups metrics by scope type (Position, Portfolio, Transaction)

### Users App
- **Primary Purpose**: User authentication and profiles
- **Dependencies**: None
- **Key Features**:
  - User authentication
  - Profile management

## Key Integration Points

1. **Portfolio → Metrics**
   - Position detail view includes metric components
   - Metric values are associated with positions
   - Computed metrics use position data

2. **Metrics → Portfolio**
   - Metric values reference positions
   - Metric types are displayed in portfolio views

3. **Users → Portfolio**
   - Portfolios are associated with users
   - Authentication required for portfolio operations

## Template Structure

1. **Base Template**
   - Location: `templates/base.html`
   - Purpose: Provides common layout and includes

2. **App-Specific Templates**
   - Each app has its own template directory
   - Components are stored in `components/` subdirectories
   - Templates follow consistent naming conventions

3. **Shared Components**
   - Metrics components can be included in portfolio templates
   - Common styling and layout patterns

## URL Structure

```
/                           # Home page
├── portfolio/              # Portfolio management
│   ├── create/            # Create portfolio
│   └── <uuid>/           # Portfolio detail
│       ├── position/     # Position management
│       └── transaction/  # Transaction management
│
├── metrics/               # Metrics management
│   ├── create/           # Create metric type
│   └── <uuid>/          # Metric operations
│
└── accounts/             # User management
    ├── login/
    ├── logout/
    └── profile/
```

## Related Documentation
- [Data Model](Data%20Model.md) - Database schema and relationships
- [Templates](templates.md) - Template structure and components
- [Design Document](Design%20Document.md) - Application design and features 