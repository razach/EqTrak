# Design Document for Stock Tracking Web App

[← Back to Documentation](README.md) | [Templates](templates.md) | [Data Model](Data%20Model.md)

## Overview
This web app is designed to help users track their equity positions, analyze stock valuation metrics, and record forecasts on stock valuations. The app will provide tools to manage portfolios, evaluate past investment decisions, and make informed forecasts based on user-defined assumptions. Below is a detailed design document outlining the app's key features, architecture, and user interface.

---

## Key Features

### 1. **Portfolio Management & Performance Benchmarking**
- **Purpose**: Allow users to record and track their equity positions and Allow users to compare their portfolio performance against market benchmarks.
- **Core Functionalities**:
  - Add, edit, or delete positions (e.g., stock ticker, number of shares, purchase price).
  - Display portfolio performance with metrics like total value, unrealized gains/losses, and allocation percentages.
  - Provide historical performance charts for individual stocks and the overall portfolio.
  - Compare to benchmarks such an indexes
	  - Include common benchmarks like S&P 500, NASDAQ, or sector-specific indices.
	  - Display performance metrics such as annualized returns, volatility, and Sharpe ratio.
- **Data Requirements**:
  - User-specific portfolio data stored in a secure database.
  - Real-time or delayed stock price updates via an API (e.g., Alpha Vantage, IEX Cloud).
    
- **Benefit**: Helps users evaluate whether their portfolio is outperforming or underperforming the market.

### 2. **Scorekeeper for Investment Decisions**
- **Purpose**: Evaluate the quality of past buy/sell decisions based on subsequent price movements.
- **Core Functionalities**:
  - Track every buy/sell decision with details like the date, price, and quantity.
  - Detailed notes field
  - Compare the stock's performance after the decision (e.g., price change after 1 month, 6 months, etc.).
  - Assign a score (e.g., percentage gain/loss) to each decision and provide aggregate statistics on decision quality.
- **Data Requirements**:
  - Historical stock price data for comparison.
  - User-specific transaction history stored securely.

### 3. **Valuation Metrics Analysis**
- **Purpose**: Help users evaluate whether it's a good time to buy or sell based on historical valuation data.
- **Core Functionalities**:
  - Display recent history of key valuation metrics (e.g., P/E ratio, P/B ratio, dividend yield).
  - Provide visualizations like line charts or bar graphs for trends over time.
  - Show the historical ranges for the valuation metrics
  - Allow users to set custom thresholds for "good buy" or "good sell" signals (e.g., P/E below a certain level).
- **Data Requirements**:
  - Historical financial data for stocks sourced from APIs or financial databases.
  - User-configurable thresholds stored in the database.

### 4. **Forecasting Tool**
- **Purpose**: Allow users to create forecasts by inputting assumptions about growth, profitability, and valuation multiples.
- **Core Functionalities**:
	- 1. Valuation / Hypothesis Store
		  - Input fields for growth rate (%), profit margin (%), and P/E multiple assumptions.
		  - Calculate projected revenue, earnings per share (EPS), and share price based on inputs.
		  - Display results in both tabular and graphical formats (e.g., projected share price vs. time).
		  - Save forecasts for future reference and comparison with actual outcomes.
		  - Allow users to set price alerts for specific stocks (e.g., "Notify me when the stock hits $X").
		  - Include valuation-based alerts (e.g., P/E ratio exceeds a certain threshold).
		  - Push notifications or emails to inform users when their exit criteria are met.
	- 2. Valuation Sense Check
		- Same inputs fields as above, but with Share Price filled in
		- Allow back calculating the EPS series (short, medium, long term), risk (discount), PE, PS or profit margin.

- **Data Requirements**:
  - User-defined input data stored in the database.
  - Calculation engine to process inputs and generate outputs.

## Market Data Integration

### Provider Architecture

The Market Data app implements a provider pattern to allow for flexible data sourcing:

1. **Base Provider Interface**
   - Defined in `market_data/providers/base.py`
   - Abstract methods for fetching securities and prices
   - Standard response format regardless of source

2. **Provider Implementations**
   - Yahoo Finance (`market_data/providers/yahoo.py`)
   - Alpha Vantage (`market_data/providers/alpha_vantage.py`)
   - Future providers can be added with minimal changes

3. **Provider Configuration**
   - System-level provider selection via settings
   - User-level provider preferences override system defaults
   - Encrypted storage of provider API keys
   - Factory pattern for provider selection based on context

```python
# Provider selection example
MARKET_DATA_PROVIDER = 'yahoo'  # System default, can be overridden by user preferences
```

4. **User Provider Preferences**
   - Users can select their preferred data provider
   - API key management for providers requiring authentication
   - Encrypted storage of sensitive API credentials
   - Dynamic form UI that adapts to selected provider

### Market Data Updates Control

The application provides a user-friendly toggle to enable or disable market data updates system-wide:

1. **Toggle Interface**
   - Available on the Settings page
   - Simple switch UI for immediate control
   - Visual feedback on current status

2. **Implementation Details**
   - Singleton settings model (`MarketDataSettings`) stores toggle state
   - Centralized checking through `is_updates_enabled()` method
   - Graceful degradation when updates are disabled (shows cached data)
   - User-specific toggle to override system settings (when enabled)

3. **API Call Prevention**
   - When disabled, prevents external API calls from all app components
   - Management commands respect the toggle (with override option)
   - Service methods check toggle state before external requests
   - Decorator pattern for consistent access control

### Data Flow Between Apps

1. **Market Data → Portfolio Integration**
   - Securities from Market Data app are referenced by Position model
   - Position values are calculated using latest prices
   - Positions display current market values based on PriceData

2. **Market Data → Metrics Integration**
   - Price-dependent metrics use latest security prices
   - Performance calculations reference historical price data
   - Market value change metrics use price history

3. **Data Refresh Workflow**
   - Scheduled tasks update price data periodically
   - Manual refresh triggers are available via admin interface
   - Price updates trigger position value recalculations

### Caching Strategy

To minimize external API calls:

1. **Historical Data**
   - Full history fetched once per security
   - Daily incremental updates for active securities

2. **Recency Rules**
   - Market prices considered stale after configurable time
   - Different freshness requirements for different use cases
   - Single price fetch per day unless forced refresh

3. **Cache Invalidation**
   - Time-based expiry for current prices
   - Manual refresh options for immediate updates
   - Database storage of fetched prices for reuse

### Error Handling

Market data failures are managed through:

1. **Retries and Fallbacks**
   - Failed API calls retried with exponential backoff
   - Multiple provider support for critical data

2. **Staleness Indicators**
   - UI indicates when prices are outdated
   - System alerts for persistent data failures

3. **Degraded Operation Mode**
   - System continues to function with outdated prices
   - Clear indicators when operating with stale data

## Related Documentation
- [Data Model](Data%20Model.md) - Database schema and relationships
- [Templates](templates.md) - Template structure and components