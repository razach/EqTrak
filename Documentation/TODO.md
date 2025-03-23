# General App TODO

## Overview
This document outlines the remaining tasks needed to fully integrate the market_data app with the rest of the application.


### Portfolio APP Updates
This is the main / core app within the django project.

## Priority Tasks

- [ ] **Modular Templates**: Implement a general UI framework that allows other apps to keep code contained within each module.
    Goal: Allows apps to be turned on or off and have the UI update itself accordinaly
- [ ] **UI Rebuild**: Rebuild the UI to move the detailed metric information to a settings section or even a detailed metric section.


### User APP Updates
This is the core app that handles all user level config and metadata

- [x] **App Toogles**: Implement a user specific config section with the ability to turn on and off specific app modules.
    Goals: Allows the user to turn on and off features they don't need or want. Core app functions of portfolio and metrics cannot be turned off


### Metric Module
This is the core app that keeps track of the system metrics and implements the auto calcualtion logic

## Priority Tasks

- [X] **Global Metric Registry**: Implement a way to keep track of register metrics and allow other apps to check if they are available.
    Seems to be implemented by calling get_system_metric get_system_metric() and get_metrics_for_scope()
- [ ] **Cash Balance Function**: Implement cash balance function at the portfolio level based on sale transaction

### Performance Module
This module allow for gain/loss calculations at the portfolio, position, and transaction level. The idea is that if the user turns this feature off, then no gain/loss metrics are shown.

## Priority Tasks

- [WIP] **Basic MVP**: Stand up a new app and give it the ability to calculate gain and losses at each of the 3 levels. 
  - Implementation plan created in Documentation/PERFORMANCE_MODULE.md
  - Working on the Django app structure and models
- [WIP] **Performance App Toggle**: A way to turn on and off the module
  - Implementation will follow the pattern in APP_TOGGLES.md


### Suggested Future Improvements

- [ ] **Annualized performance**: Functionality to take time into considerations and shows performance over time. Allows apples to apples comparisons.
- [ ] **Benchmark**: Show gains against a benchmark that the user can select. 

### Valuation Module

## Priority Tasks

- [ ] **Basic MVP**: Stand up a new app and give it the ability to add in a few custom metrics
- [ ] **Valueation App Toggle**: A way to turn on and off the module


### User Defined Metric Module
This is a minor app that handles user level custom metrics

## Priority Tasks

- [x] **User Defined Metrics**: Implement functionality in a separate app for users to define and track custom metrics
- [x] **Move the add metric functionality over**: Move the add new metric functionality over to this separate app.
- [ ] **Code review and clean up**: Conduct a general code review and clean things up.

### Suggested Future Improvements

- [ ] **Formula Validation**: Add validation for user-defined formulas to prevent errors
- [ ] **Formula Testing Tool**: Create a testing interface where users can try formulas before saving
- [ ] **Sharing Custom Metrics**: Allow users to share their custom metrics with other users
- [ ] **Metric Categories**: Add ability to categorize custom metrics for better organization
- [ ] **Custom Metric Templates**: Provide pre-built templates for common custom metrics
- [ ] **Conditional UI Display**: Update all UI elements to respect the user_metrics_enabled setting
- [ ] **Improved Error Handling**: Add better error handling for formula execution failures


### Market Data Integration
This is the minor app that handles the API calls to get data from external sources

## Priority Tasks

### Add Position Process
- [ ] **Metric to datafeed map**: Create a yaml based mapping document to tie specific metrics to data feed implmentation
- [ ] **Position Form Enhancement**: Update the Position creation form to validate ticker symbols against market_data.Security
- [ ] **Auto-populate Fields**: When a user enters a ticker symbol, auto-populate security name and security type
- [ ] **Market Price Integration**: Add option to fetch current market price when creating a position
- [ ] **Position Model Update**: Ensure Position model correctly interacts with market_data.Security through the ticker field

### Portfolio Views
- [ ] **Portfolio Detail Page**: Update to show current market values for all positions
- [ ] **Portfolio Summary Metrics**: Add total market value and unrealized gain/loss metrics
- [ ] **Bulk Update**: Add functionality to update all positions' market data in a portfolio at once
- [x] **Market Data Toggle**: Add UI controls to enable/disable market data updates system-wide

### Position Detail View
- [ ] **Price History Chart**: Add price history chart to position detail page
- [ ] **Historical Performance**: Show position performance against historical market data
- [ ] **Related Securities**: Show related securities (e.g., sector peers)

### Transaction Experience
- [ ] **Market Price Button**: Add button to fetch current market price when creating transactions
- [ ] **Market Status Indicator**: Show if market is open/closed during transaction creation

## Secondary Tasks

### Search and Discovery
- [ ] **Security Search**: Implement search functionality for securities
- [ ] **Security Detail Page**: Create a page to view detailed information about a security
- [ ] **Security List**: Admin page listing all tracked securities

### Data Management
- [ ] **Scheduled Updates**: Configure recurring tasks to update price data
- [ ] **Data Health Monitoring**: Add admin views to monitor data freshness
- [ ] **Price Data Cleanup**: Implement data retention policies
- [x] **Data Update Control**: Implement toggle system to enable/disable external API calls

### User Experience Improvements
- [ ] **Loading States**: Add loading indicators during market data fetching
- [ ] **Error Handling**: Improve error handling for market data failures
- [ ] **Stale Data Indicators**: Clearer visual indicators for stale data

### Performance Optimization
- [ ] **Database Indexing**: Review and optimize indices for market_data models
- [ ] **Query Optimization**: Review and optimize queries in MarketDataService
- [ ] **Caching**: Implement response caching for frequent market data requests

## Technical Debt
- [ ] **Test Coverage**: Increase test coverage for market_data app
- [ ] **Documentation**: Update API documentation for MarketDataService
- [ ] **Provider Abstraction**: Review and improve the provider abstraction
- [ ] **Error Logging**: Enhance error logging for market data operations

