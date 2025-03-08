# Market Data Integration TODO

## Overview
This document outlines the remaining tasks needed to fully integrate the market_data app with the rest of the application.

## Priority Tasks

### Add Position Process
- [ ] **Position Form Enhancement**: Update the Position creation form to validate ticker symbols against market_data.Security
- [ ] **Auto-populate Fields**: When a user enters a ticker symbol, auto-populate security name and security type
- [ ] **Market Price Integration**: Add option to fetch current market price when creating a position
- [ ] **Position Model Update**: Ensure Position model correctly interacts with market_data.Security through the ticker field

### Portfolio Views
- [ ] **Portfolio Detail Page**: Update to show current market values for all positions
- [ ] **Portfolio Summary Metrics**: Add total market value and unrealized gain/loss metrics
- [ ] **Bulk Update**: Add functionality to update all positions' market data in a portfolio at once
- [ ] **Data Refresh Buttons**: Add UI controls to manually refresh market data

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
