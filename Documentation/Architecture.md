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
│   ├── providers.py      # Provider registry for metric calculations
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
├── performance/           # Performance tracking app 
│   ├── models.py         # PerformanceSettings, PerformanceMetric models
│   ├── views.py          # Performance-related views
│   ├── urls.py           # Performance URL patterns
│   ├── services.py       # Performance calculation services
│   ├── integration.py    # Integration with metrics system
│   ├── providers.py      # Performance metric providers
│   ├── signals.py        # Performance-related signals
│   ├── patches.py        # Runtime patches for metrics
│   ├── templatetags/     # Custom template tags
│   └── templates/        # Performance templates
│       └── performance/  
│           └── components/
│               └── portfolio_performance_card.html
│
├── market_data/           # Market data app
│   ├── models.py         # Security, PriceData models
│   ├── views.py          # Market data views
│   ├── urls.py           # Market data URL patterns
│   ├── services.py       # Market data services
│   ├── signals.py        # Market data signals
│   ├── providers/        # Data provider implementations
│   │   ├── base.py      # Provider base class
│   │   └── yahoo.py     # Yahoo Finance provider
│   ├── tasks.py         # Async tasks for data fetching
│   └── templates/
│       └── market_data/  # Market data templates
│           ├── security_list.html
│           └── price_chart.html
│
├── user_metrics/          # User-defined metrics app
│   ├── models.py         # UserMetric, UserMetricValue models
│   ├── views.py          # User metric views
│   ├── urls.py           # User metric URL patterns
│   ├── forms.py          # User metric forms
│   └── templates/        # User metric templates
│       └── user_metrics/
│           ├── user_metric_form.html
│           └── user_metric_list.html
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
  - Market Data app for security prices
  - Performance app for gain/loss calculations
- **Key Features**:
  - Portfolio CRUD operations with UUID primary keys
  - Position management with cost basis tracking
  - Transaction tracking with impact calculation
  - Cash balance management

### Metrics App
- **Primary Purpose**: Handles metric types and values
- **Dependencies**:
  - Portfolio app for position, portfolio, and transaction data
  - Market Data app for price-based metrics
- **Key Features**:
  - Metric type definitions (system and user-defined)
  - Metric value tracking with support for:
    - Numeric and memo-type values
    - Computed metrics with dependencies
    - Forecasting with scenarios
    - Confidence scoring
  - Automated computation system
  - Validation framework
  - Provider system for external metric calculations
- **Global Context**:
  - Provides metric types to all templates via context processor
  - Groups metrics by scope type (Position, Portfolio, Transaction)

### Performance App
- **Primary Purpose**: Calculates and tracks investment performance
- **Dependencies**:
  - Portfolio app for positions and transactions
  - Metrics app for storing performance values
  - Market Data app for current prices
- **Key Features**:
  - Gain/loss calculation at portfolio, position, and transaction levels
  - Time-weighted return calculation
  - Performance metrics with percentage and absolute values
  - Feature toggle system (system and user level)
  - Provider registration for metrics integration
  - Integration with metrics app for display
  - UUID support via ContentTypes framework

### Market Data App
- **Primary Purpose**: Retrieves and manages security price data
- **Dependencies**:
  - None (other apps depend on it)
- **Key Features**:
  - Extensible provider architecture
  - Yahoo Finance integration
  - Historical price data retrieval
  - Price caching system
  - Security management
  - Data refresh scheduling
  - Signals for price updates
  - Configuration via fixtures
- **Provider System**:
  - Base provider interface
  - Provider-specific implementations
  - Configuration-based provider selection

### User Metrics App
- **Primary Purpose**: Allows users to define and track custom metrics
- **Dependencies**:
  - Metrics app for core functionality
  - Portfolio app for applying metrics
- **Key Features**:
  - Custom metric definitions
  - User-defined formulas
  - Metric sharing between users
  - Visualization options
  - Integration with system metrics

### Users App
- **Primary Purpose**: User authentication and profiles
- **Dependencies**: None
- **Key Features**:
  - User authentication
  - Profile management
  - App feature access control
  - User preferences storage

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

4. **Market Data → Portfolio**
   - Provides security prices for positions
   - Updates position values based on latest prices
   - Signals trigger recalculation when prices change

5. **Market Data → Metrics**
   - Supplies price data for price-based metrics
   - Enables performance calculations
   - Price update signals trigger metric updates

6. **Performance → Metrics**
   - Registers metric calculation providers
   - Calculates performance metrics (gain/loss, returns)
   - Integrates with metrics storage system
   - Performance toggle controls metric visibility

7. **User Metrics → Metrics**
   - Extends the core metrics system with user definitions
   - Provides custom calculation formulas
   - Renders in the same UI components

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
   - Performance components provide gain/loss displays
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
├── performance/           # Performance management
│   ├── toggle/           # Toggle performance features
│   └── settings/         # Performance settings
│
├── user-metrics/          # User-defined metrics
│   ├── create/           # Create user metric
│   └── <uuid>/          # User metric operations
│
├── market-data/           # Market data management
│   ├── securities/       # Security management
│   │   ├── create/      # Create security
│   │   └── <uuid>/     # Security detail
│   ├── refresh/         # Manual data refresh
│   └── api/             # API endpoints for price data
│
└── accounts/             # User management
    ├── login/
    ├── logout/
    └── profile/
```

## Provider System

The application implements a provider system that allows for clean separation of concerns between the metrics storage system and domain-specific calculation logic:

### Provider Architecture

```
                  +-------------------+
                  |                   |
                  |  Metrics System   |
                  |                   |
                  +--------+----------+
                           |
                           | Registers
                           | providers
                           v
             +-------------+-------------+
             |                           |
             |  metrics/providers.py     |
             |  Provider Registry        |
             |                           |
             +--+----------+----------+--+
                |          |          |
                |          |          |
     +----------v-+  +-----v------+  +v--------------+
     |            |  |            |  |               |
     | Performance|  | Market     |  | User-defined  |
     | Providers  |  | Data       |  | Metric        |
     |            |  | Providers  |  | Providers     |
     +------------+  +------------+  +---------------+
```

### Key Components

1. **Provider Registry** (metrics/providers.py)
   - Central registry for metric calculation functions
   - Simple dictionary-based lookup system
   - Allows external apps to register calculation providers
   ```python
   METRIC_PROVIDERS = {}  # Dictionary mapping metric names to provider functions
   
   def register_provider(metric_name, provider_function):
       """Register a function that can compute values for a specific metric"""
       global METRIC_PROVIDERS
       METRIC_PROVIDERS[metric_name] = provider_function
   ```

2. **Provider Registration** (performance/providers.py)
   - Domain-specific apps register their calculation functions
   - Registration happens during app initialization (in AppConfig.ready())
   - Maps metric names to calculation functions
   ```python
   def register_providers():
       """Register all performance metric providers with the metrics system"""
       from metrics.providers import register_provider
       
       # Register position gain/loss providers
       register_provider(POSITION_GAIN, PerformanceCalculationService.get_position_gain_percentage)
       register_provider(POSITION_GAIN_ABSOLUTE, PerformanceCalculationService.get_position_gain_absolute)
   ```

3. **Integration Functions** (performance/integration.py)
   - Clean interface between domain logic and metrics storage
   - Handles converting domain values to metric values
   - Manages metric creation/updating
   ```python
   def store_position_gain_percentage(position, value):
       """Store position gain/loss percentage in the metrics system"""
       from metrics.models import MetricType, MetricValue
       metric_type = MetricType.objects.get(name=POSITION_GAIN)
       MetricValue.objects.update_or_create(
           metric_type=metric_type,
           position=position,
           defaults={'value': value}
       )
   ```

4. **Computation Flow**
   - Metrics app tries to find a provider for a requested metric
   - If found, calls the provider function to get the value
   - If no provider, falls back to built-in calculation methods
   - Providers are domain-specific and encapsulate business logic
   ```python
   def compute_value(self, target_object):
       """First try using a registered provider, then fall back to internal methods"""
       from metrics.providers import compute_metric_value
       
       # Try using a provider first
       result = compute_metric_value(self.name, target_object)
       if result is not None:
           return result
           
       # Fall back to built-in computation methods
       # ...
   ```

### Benefits

1. **Modularity**
   - Domain-specific calculation logic stays in relevant apps
   - Metrics app remains agnostic about calculation implementation
   - Clean separation of responsibilities

2. **Extensibility**
   - New apps can register their own providers
   - Metrics system can be extended without modification
   - Pluggable architecture for different calculation methods

3. **Simplified Testing**
   - Provider functions can be tested in isolation
   - Mock providers can be registered for testing
   - Reduced dependencies between systems

### Implementation Example

```python
# In metrics/providers.py
METRIC_PROVIDERS = {}

def register_provider(metric_name, provider_function):
    """Register a provider function for a specific metric"""
    global METRIC_PROVIDERS
    METRIC_PROVIDERS[metric_name] = provider_function
    
def compute_metric_value(metric_name, target_object):
    """Compute a metric value using the registered provider"""
    provider = get_provider(metric_name)
    if provider:
        return provider(target_object)
    return None

# In domain-specific app (e.g., performance/providers.py)
def register_providers():
    """Register domain-specific providers"""
    from metrics.providers import register_provider
    register_provider('Position Gain/Loss', PerformanceCalculationService.get_position_gain_percentage)
    register_provider('Portfolio Return', PerformanceCalculationService.get_portfolio_return_percentage)
    
# In app initialization (e.g., performance/apps.py)
class PerformanceConfig(AppConfig):
    name = 'performance'
    
    def ready(self):
        """Initialize the app when Django starts"""
        from .providers import register_providers
        register_providers()
```

## Configuration and Fixtures

The application uses Django fixtures for configuration data, allowing for:

1. **Standard Metric Types**
   - Core metric types defined in `metrics/fixtures/standard_metrics.json`
   - Loaded during initial setup and migrations

2. **Performance Metrics**
   - Performance-related metrics in `performance/fixtures/performance_metrics.json`
   - Toggle-able via management commands

3. **Market Data Configuration**
   - Provider settings in `market_data/fixtures/provider_config.json`
   - Refresh intervals and API settings

### Management Commands

Various management commands facilitate configuration:

```bash
# Metrics configuration
python manage.py configure_metrics --load --module=metrics

# Performance features
python manage.py toggle_performance_metrics --activate

# Market data refresh
python manage.py refresh_market_data --all
```

## Related Documentation
- [Data Model](Data%20Model.md) - Database schema and relationships
- [Templates](templates.md) - Template structure and components
- [Design Document](Design%20Document.md) - Application design and features
- [PERFORMANCE_MODULE.md](PERFORMANCE_MODULE.md) - Performance app details
- [APP_TOGGLES.md](APP_TOGGLES.md) - Feature toggle system

## Docker Development

### Local Development Environment
Docker is used primarily as a local development environment that provides consistent tooling and dependencies across developer machines, using a simple Dockerfile with volume mapping.

### Development Setup Files
1. **Dockerfile**
   - Base image: Python 3.11 slim
   - Development dependencies
   - Application setup
   - Entrypoint configuration
2. **docker-entrypoint.sh**
   - Database migrations
   - Static file collection
   - Superuser creation
   - Application startup

### Quick Start Guide
1. **Prerequisites**
   - Docker Desktop (Mac/Windows) or Docker Engine (Linux)
   - Git

2. **Environment Setup**
   ```bash
   # Clone repository
   git clone [repository-url]
   cd EqTrak

   # Build the Docker image
   docker build -t eqtrak-dev .
   
   # Run with volume mapping to enable real-time development
   docker run -d -it -v "$(pwd):/workspace" -p 8000:8000 eqtrak-dev
   ```

3. **Development Workflow**
   - Local code is mounted into the container via volume mapping
   - Code changes are reflected immediately (hot-reload)
   - Access logs via `docker logs <container_id>`

4. **Common Tasks**
   ```bash
   # Get container ID
   docker ps
   
   # Create migrations
   docker exec <container_id> python manage.py makemigrations

   # Apply migrations
   docker exec <container_id> python manage.py migrate

   # Create superuser
   docker exec -it <container_id> python manage.py createsuperuser

   # Collect static files
   docker exec <container_id> python manage.py collectstatic
   ```

5. **Environment Variables**
   Pass environment variables directly in the docker run command:
   ```bash
   docker run -d -it -v "$(pwd):/workspace" -p 8000:8000 \
     -e DEBUG=True \
     -e SECRET_KEY=your-dev-secret-key \
     -e ALLOWED_HOSTS=localhost,127.0.0.1 \
     eqtrak-dev
   ```

6. **Accessing the Application**
   - Application: http://localhost:8000
   - Admin Panel: http://localhost:8000/admin

### Best Practices
1. Don't expose sensitive information in Dockerfile or commands
2. Use environment variables for configuration
3. Use volume mounts for development to edit code without container rebuilds
4. Consider setting up .env files for local development
5. Monitor container logs for issues
6. Restart the container after major dependency changes