# General App TODO

## Overview
This document outlines the remaining tasks needed to fully integrate the market_data app with the rest of the application.


### Portfolio APP Updates
This is the main / core app within the django project.

## Priority Tasks

- [ ] **Modular Templates**: Implement a general UI framework that allows other apps to keep code contained within each module.
    Goal: Allows apps to be turned on or off and have the UI update itself accordinaly


### User APP Updates
This is the core app that handles all user level config and metadata

- [X] **App Toogles**: Implement a user specific config section with the ability to turn on and off specific app modules.
    Goals: Allows the user to turn on and off features they don't need or want. Core app functions of portfolio and metrics cannot be turned off
- [X] **Market Data Provider Preferences**: Implement user-specific provider selection and API key management.
    Goals: Allow users to choose their preferred data sources and provide API keys


### Metric Module
This is the core app that keeps track of the system metrics and implements the auto calcualtion logic

## Priority Tasks

- [ ] **Cash Balance Function**: Implement cash balance function at the portfolio level based on sale transaction


### User Defined Metric Module
This is a minor app that handles user level custom metrics

## Priority Tasks

- [ ] **User Defined Metrics**: Implement functionality in a separate app for users to define and track custom metrics
- [ ] **Move the add metric functionality over**: Move the add new metric functionality over to this separate app.


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

### Provider Management
- [x] **Provider Selection**: Allow users to select their preferred market data provider
- [x] **API Key Management**: Add secure storage for user-provided API keys
- [x] **Provider Factory**: Implement factory pattern for selecting providers based on user preference
- [ ] **Provider Comparison**: Add tools to compare data quality between providers

### Performance Optimization
- [ ] **Caching Strategy**: Implement database caching for market data to reduce API calls (I believe there is a defect with the current implementation)
- [ ] **Database Indexing**: Review and optimize indices for market_data models
- [ ] **Query Optimization**: Review and optimize queries in MarketDataService

## Technical Debt
- [ ] **Test Coverage**: Increase test coverage for market_data app
- [ ] **Documentation**: Update API documentation for MarketDataService
- [x] **Provider Abstraction**: Review and improve the provider abstraction
- [ ] **Error Logging**: Enhance error logging for market data operations

