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

### Using Docker (Recommended)
1. Prerequisites:
   - Docker
   - Docker Compose

2. Quick Start:
   ```bash
   # Clone the repository
   git clone [repository-url]
   cd EqTrak

   # Start the development environment
   docker-compose up --build
   ```

3. Access:
   - Application: http://localhost:8000
   - Admin Panel: http://localhost:8000/admin

### Traditional Setup
See [Architecture](Architecture.md#development-setup) for traditional setup instructions.

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