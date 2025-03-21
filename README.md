# EqTrak - Stock Portfolio Tracking & Analysis Platform

## Overview
EqTrak is a comprehensive web application designed to help investors track, analyze, and make informed decisions about their equity investments. The platform combines portfolio management, performance tracking, valuation analysis, and forecasting tools in one integrated solution.

## Documentation
📚 [View Full Documentation](Documentation/README.md)

### Quick Links
- [Design Document](Documentation/Design%20Document.md) - Detailed feature specifications and architecture
- [Data Model](Documentation/Data%20Model.md) - Database schema and relationships
- [Templates](Documentation/templates.md) - Frontend template structure and components

## Key Features

### 📊 Portfolio Management & Benchmarking
- Track multiple investment portfolios
- Real-time position monitoring
- Performance comparison against market benchmarks
- Portfolio allocation visualization
- Historical performance analytics

### 📈 Investment Decision Scorekeeper
- Record and evaluate buy/sell decisions
- Track performance of individual trades
- Maintain detailed transaction notes
- Generate decision quality metrics

### 💹 Valuation Analytics
- Monitor key valuation metrics (P/E, P/B, dividend yield)
- Historical valuation trend analysis
- Custom threshold alerts
- Comparative analysis tools

### 🎯 Forecasting Tools
1. **Valuation/Hypothesis Store**
   - Create and save price forecasts
   - Input custom growth and profitability assumptions
   - Set price and valuation alerts
   
2. **Valuation Sense Check**
   - Back-calculate required growth rates
   - Analyze implied valuations
   - Risk and return scenario modeling

## Technical Stack

- **Backend**: Django (Python web framework)
- **Database**: SQLite (Development), PostgreSQL (Production)
- **Frontend**: 
  - Bootstrap 5 for responsive UI
  - JavaScript for interactivity
  - Django Templates for server-side rendering
- **API Integration**: Financial market data providers

## Development Setup

### Option 1: Using Docker (Recommended)
1. **Prerequisites**
   - Docker

2. **Quick Start with Docker**
   ```bash
   # Clone the repository
   git clone [repository-url]
   cd EqTrak

   # Build the Docker image
   docker build -t eqtrak-dev .
   
   # Run with volume mapping to enable real-time development
   docker run -d -it -v "$(pwd):/workspace" -p 8000:8000 eqtrak-dev
   ```

3. **Access the application**
   - Visit `http://localhost:8000` to access the application
   - Admin interface available at `http://localhost:8000/admin`

4. **Common Docker Commands**
   ```bash
   # View running containers
   docker ps
   
   # Execute commands in container
   docker exec -it <container_id> python manage.py migrate
   docker exec -it <container_id> python manage.py createsuperuser
   
   # View logs
   docker logs <container_id>
   
   # Stop container
   docker stop <container_id>
   ```

### Option 2: Traditional Setup
1. **Prerequisites**
   - Python 3.8+
   - pip (Python package manager)
   - Virtual environment tool (venv recommended)

2. **Installation**
   ```bash
   git clone [repository-url]
   cd EqTrak
   ```

3. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Setup database**
   ```bash
   python manage.py migrate
   ```

6. **Create a superuser (optional)**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run development server**
   ```bash
   python manage.py runserver
   ```

Visit `http://localhost:8000` to access the application.

## Project Status
🚧 Currently in Development

### Current Focus
- Core portfolio management features
- Basic metric tracking
- User authentication and authorization
- Template structure and styling

### Coming Soon
- Advanced analytics
- API integrations
- Real-time data updates
- Mobile responsiveness improvements

## Contributing
We welcome contributions! Please read our [contributing guidelines](Documentation/CONTRIBUTING.md) before submitting pull requests.

### Development Process
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support
For support, please:
1. Check the [documentation](Documentation/README.md)
2. Open an issue in the repository
3. Contact the development team

---
*Note: This project is under active development. Features and documentation will be updated regularly.*