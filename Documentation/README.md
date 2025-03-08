# EqTrak Documentation

Welcome to the EqTrak documentation. This documentation provides comprehensive information about the application's design, implementation, and usage.

## Core Documentation

1. [Architecture](Architecture.md)
   - Project structure
   - App interactions
   - Integration points
   - Template organization
   - URL structure
   - Docker development setup

2. [Design Document](Design%20Document.md)
   - Overview of the application
   - Key features and functionalities
   - System architecture
   - User interface design

3. [Data Model](Data%20Model.md)
   - Database schema
   - Table relationships
   - Field descriptions
   - Data types and constraints

4. [Templates](templates.md)
   - Template organization
   - Component structure
   - Usage guidelines
   - Styling conventions

## Development Setup

### Using Docker for Local Development
1. Prerequisites:
   - Docker

2. Quick Start with Docker:
   ```bash
   # Clone the repository
   git clone [repository-url]
   cd EqTrak

   # Build the Docker image
   docker build -t eqtrak-dev .
   
   # Start the development environment with volume mapping
   docker run -d -it -v "$(pwd):/workspace" -p 8000:8000 eqtrak-dev
   ```

3. Access:
   - Application: http://localhost:8000
   - Admin Panel: http://localhost:8000/admin

### Key Docker Features
- **Volume Mapping**: Local code is mounted into the container, enabling real-time code editing
- **Isolated Environment**: Consistent development environment across different machines
- **Simplified Setup**: Single Dockerfile without the overhead of docker-compose
- **Auto-reload**: Code changes are detected and the server reloads automatically

### Traditional Setup
See [Architecture](Architecture.md#development-setup) for traditional setup instructions.

## Development Roadmap

For a detailed list of upcoming tasks and planned features, see the [TODO document](TODO.md) which includes:

- Market Data Integration tasks
- UI Enhancements
- Data Management improvements
- Performance Optimization tasks

We are actively working on integrating real-time market data functionality. Check the TODO document for specific implementation plans.

## Development Resources

- [Test Users](test_users.md) (Development environment only)

## Quick Links

### For Developers
- [Project Structure](Architecture.md#project-structure)
- [App Interactions](Architecture.md#app-interactions)
- [Data Model Tables](Data%20Model.md#core-data-model)
- [Key Features](Design%20Document.md#key-features)
- [Docker Setup](Architecture.md#docker-development)

### For Template Development
- [Template Structure](Architecture.md#template-structure)
- [Template Best Practices](templates.md#best-practices)
- [Context Requirements](templates.md#context-requirements)
- [Styling Guidelines](templates.md#styling)