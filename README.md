# EqTrak - Stock Portfolio Tracking & Analysis Platform

## Overview
EqTrak is a comprehensive web application designed to help investors track, analyze, and make informed decisions about their equity investments. The platform combines portfolio management, performance tracking, valuation analysis, and forecasting tools in one integrated solution.

## Documentation
📚 [View Full Documentation](Documentation/README.md)

### Quick Links
- [Development Setup](Documentation/DEVELOPMENT_SETUP.md) - Setting up your development environment
- [Architecture](Documentation/Architecture.md) - Application architecture and design patterns
- [Data Model](Documentation/Data%20Model.md) - Database schema and relationships
- [Performance Module](Documentation/PERFORMANCE_MODULE.md) - Performance tracking implementation
- [Changelog](Documentation/CHANGELOG.md) - Recent fixes and improvements

## Key Features

### 📊 Portfolio Management & Performance Tracking
- Track multiple investment portfolios with positions and transactions
- Real-time position monitoring with current values
- Performance metrics with gain/loss calculations at portfolio, position, and transaction levels
- Comprehensive transaction history and analysis
- Custom user-defined metrics for personalized tracking

### 📈 Market Data Integration
- Automated market price tracking from reliable sources
- Detailed stock information and fundamental data
- Flexible update control settings
- Manual and automatic data updates with configurable frequency

### 💹 Modular Architecture
- Core tracking functionality with extensible modules
- Performance module for gain/loss calculations
- Custom metrics definition and management
- Feature toggles to enable/disable functionality by module or user

## Technology Stack

- **Backend**: Django 4.2, Python 3.9+
- **Frontend**: Bootstrap 5, Vanilla JavaScript
- **Database**: SQLite (development), PostgreSQL (production)
- **Deployment**: Docker, Gunicorn

## Getting Started

See [DEVELOPMENT_SETUP.md](Documentation/DEVELOPMENT_SETUP.md) for detailed instructions.

### Quick Start

```bash
# Clone the repository
git clone https://github.com/yourusername/eqtrak.git
cd eqtrak

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup database and load initial data
./EqTrak/reset_db_with_testusers.sh

# Start development server
cd EqTrak
python manage.py runserver
```

## Architecture Overview

EqTrak is organized into several key modules:

- **Portfolio**: Core portfolio, position, and transaction functionality
- **Metrics**: System for defining, calculating, and displaying metrics
- **Market Data**: Integration with market data providers
- **Performance**: Gain/loss calculations and performance tracking
- **User Metrics**: Custom user-defined metric creation and management

For more details on the architecture, see [Architecture.md](Documentation/Architecture.md).

## Recent Improvements (v0.2.0)

The latest version includes important fixes to the Performance module:

- **UUID Storage**: Fixed performance metric storage by changing `object_id` from `PositiveIntegerField` to `CharField(max_length=40)` to properly handle UUID primary keys
- **Primary Key References**: Corrected references in calculation services from `.id` to model-specific primary key fields (`portfolio_id`, `position_id`, `transaction_id`)
- **Template Handling**: Improved template conditional logic for properly evaluating performance metric access
- **Patching Mechanism**: Refactored the patch mechanism for `MetricType.get_system_metric` to handle class method arguments correctly

See the [Changelog](Documentation/CHANGELOG.md) for complete details of recent fixes.

## Development Approach

EqTrak uses a fixture-based approach for configuration:
- Schema changes in migrations
- Configuration data in JSON fixtures
- Automatic loading at application startup

This approach keeps migrations clean and makes configuration changes easier to manage.

## Documentation

- [Development Setup](Documentation/DEVELOPMENT_SETUP.md): Setting up the development environment
- [Changelog](Documentation/CHANGELOG.md): History of changes and fixes
- [Performance Module](Documentation/PERFORMANCE_MODULE.md): Performance tracking features
- [Troubleshooting](Documentation/DEVELOPMENT_SETUP.md#troubleshooting): Common issues and solutions

## Testing

```bash
# Run test suite
python manage.py test
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support
For support, please:
1. Check the [documentation](Documentation/README.md)
2. Review the [troubleshooting guide](Documentation/DEVELOPMENT_SETUP.md#troubleshooting)
3. Open an issue in the repository
4. Contact the development team

---
*Note: This project is under active development. Features and documentation will be updated regularly.*