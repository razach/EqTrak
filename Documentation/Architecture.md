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
├── market_data/           # Market data app
│   ├── models.py         # Security, PriceData models
│   ├── views.py          # Market data views
│   ├── urls.py           # Market data URL patterns
│   ├── providers/        # Data provider implementations
│   │   ├── base.py      # Provider base class
│   │   └── yahoo.py     # Yahoo Finance provider
│   ├── tasks.py         # Async tasks for data fetching
│   └── templates/
│       └── market_data/  # Market data templates
│           ├── security_list.html
│           └── price_chart.html
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
- **Key Features**:
  - Portfolio CRUD operations
  - Position management
  - Transaction tracking

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
- **Global Context**:
  - Provides metric types to all templates via context processor
  - Groups metrics by scope type (Position, Portfolio, Transaction)

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
- **Provider System**:
  - Base provider interface
  - Provider-specific implementations
  - Configuration-based provider selection

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

4. **Market Data → Portfolio**
   - Provides security prices for positions
   - Updates position values based on latest prices

5. **Market Data → Metrics**
   - Supplies price data for price-based metrics
   - Enables performance calculations 

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

## Related Documentation
- [Data Model](Data%20Model.md) - Database schema and relationships
- [Templates](templates.md) - Template structure and components
- [Design Document](Design%20Document.md) - Application design and features 

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