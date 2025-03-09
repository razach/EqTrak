# Market Data Controls

[← Back to Documentation](README.md)

## Overview

EqTrak integrates with external market data providers to fetch real-time and historical price data for securities in your portfolios. The application provides controls to manage when and how this data is fetched.

## Market Data Updates Toggle

The Market Data Updates toggle allows you to enable or disable all external API calls for market data. This feature is useful for:

- Preventing rate limit issues with data providers
- Reducing external API usage when working with historical data
- Preserving a consistent view during analysis
- Testing the application with static data

### Location

The toggle is located at the top of the Portfolios home page.

### Usage

- **Toggle On**: Enables all market data updates from external sources
- **Toggle Off**: Disables all API calls to external providers 

When disabled:
- The application will use cached price data from the database
- The data will be marked as "stale" when displayed
- No external API calls will be made from any part of the application
- The command-line tools for updates will respect this setting (unless forced)

### Technical Details

When market data updates are disabled:

1. **Position Detail Views**: 
   - Will show a notification that market data updates are disabled
   - Will use the most recent cached prices 
   - Will mark prices as "stale" in the UI

2. **Command Line Tools**:
   - The `update_market_data` management command checks the toggle
   - Use `--force` flag to override: `python manage.py update_market_data --force`

3. **MarketDataService Methods**:
   - `get_latest_price()`: Returns cached data with stale flag
   - `get_price_history()`: Returns partial data if available
   - `refresh_security_data()`: Skips update when disabled
   - `sync_price_with_metrics()`: Skips update when disabled

## Default Settings

Market data updates are enabled by default when the application is first installed.

## Admin Controls

Administrators can also control this setting via the Django admin panel:
- Navigate to Admin → Market Data → Market Data Settings
- Edit the single settings record 