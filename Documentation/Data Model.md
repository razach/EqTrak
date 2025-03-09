# Data Model Documentation

[← Back to Documentation](README.md) | [Templates](templates.md) | [Design Document](Design%20Document.md)

## Core Data Model

### **User Table**

| Field          | Type      | Required | Description                     |
|----------------|-----------|----------|---------------------------------|
| user_id        | UUID      | Yes      | Primary identifier              |
| email          | String    | Yes      | User's email address (unique)   |
| password_hash  | String    | Yes      | Securely hashed password        |
| name           | String    | Yes      | User's full name                |
| status         | Enum      | Yes      | ACTIVE, INACTIVE, SUSPENDED     |
| preferences    | JSON      | No       | User-specific app settings      |
| last_login_at  | Timestamp | No       | Most recent login time          |
| created_at     | Timestamp | Yes      | Account creation time           |
| updated_at     | Timestamp | Yes      | Last account update time        |

### **Portfolio Table**

| Field             | Type      | Required | Description                  |
| ----------------- | --------- | -------- | ---------------------------- |
| portfolio_id      | UUID      | Yes      | Primary identifier           |
| user_id           | UUID      | Yes      | Reference to owner           |
| name              | String    | Yes      | Portfolio name               |
| description       | Text      | No       | Detailed description         |
| currency          | String    | Yes      | Base currency (e.g., USD)    |
| is_active         | Boolean   | Yes      | Portfolio status             |
| created_at        | Timestamp | Yes      | Creation time                |
| updated_at        | Timestamp | Yes      | Last update time             |

### **Position Table**

| Field         | Type      | Required | Description                |
|---------------|-----------|----------|----------------------------|
| position_id   | UUID      | Yes      | Primary identifier         |
| portfolio_id  | UUID      | Yes      | Parent portfolio reference |
| ticker        | String    | Yes      | Stock symbol               |
| position_type | Enum      | Yes      | STOCK, ETF, CRYPTO, etc.   |
| shares        | Decimal   | No       | Number of shares held      |
| purchase_price| Decimal   | No       | Average purchase price     |
| cost_basis    | Decimal   | No       | Total cost basis          |
| is_active     | Boolean   | Yes      | Position status           |
| created_at    | Timestamp | Yes      | Position creation time    |
| updated_at    | Timestamp | Yes      | Last update time          |
| security      | ForeignKey| Yes      | Reference to Security     |

### **Portfolio Snapshot Table**

| Field          | Type      | Required | Description                          |
|----------------|-----------|----------|--------------------------------------|
| snapshot_id    | UUID      | Yes      | Primary identifier                   |
| portfolio_id   | UUID      | Yes      | Reference to portfolio               |
| date           | Date      | Yes      | Snapshot date                        |
| total_value    | Decimal   | Yes      | Total portfolio value               |
| cash_balance   | Decimal   | No       | Cash balance in portfolio           |
| daily_return   | Decimal   | No       | Daily return percentage             |
| indexed_return | Decimal   | No       | Indexed return value                |

### **Transaction Table**

| Field           | Type      | Required | Description                         |
|-----------------|-----------|----------|-------------------------------------|
| transaction_id  | UUID      | Yes      | Primary identifier                  |
| position_id     | UUID      | Yes      | Related position reference          |
| transaction_type| Enum      | Yes      | BUY, SELL, DIVIDEND, SPLIT, MERGER |
| quantity        | Decimal   | Yes      | Number of shares                    |
| price          | Decimal   | Yes      | Price per share                     |
| fees           | Decimal   | No       | Transaction fees                    |
| currency       | String    | Yes      | Transaction currency                |
| exchange_rate  | Decimal   | No       | Currency exchange rate if applicable|
| date           | Date      | Yes      | Transaction date                    |
| settlement_date| Date      | No       | Settlement date                     |
| status         | Enum      | Yes      | PENDING, COMPLETED, CANCELLED, FAILED|
| notes          | Text      | No       | Transaction notes                   |
| created_at     | Timestamp | Yes      | Record creation time                |

### **Metric Types Table**

| Field       | Type    | Required | Description                           |
|-------------|---------|----------|---------------------------------------|
| metric_id   | UUID    | Yes      | Primary identifier                    |
| name        | String  | Yes      | Metric name                           |
| scope_type  | Enum    | Yes      | POSITION, TRANSACTION, PORTFOLIO      |
| data_type   | Enum    | Yes      | PRICE, RATIO, VOLUME, PERCENTAGE, SHARES, CURRENCY, MEMO |
| description | Text    | No       | Description of the metric             |
| is_system   | Boolean | Yes      | System or user-defined metric         |
| tags        | String  | No       | User-defined tags for organization    |
| is_computed | Boolean | Yes      | Whether metric is computed            |
| computation_source | String | No  | Source field for computed metrics    |
| computation_order | Integer | No  | Order of computation                 |
| computation_dependencies | M2M | No | Dependencies for computed metrics   |

The `scope_type` field determines which entity the metric is associated with:
- POSITION: Metrics that track position-level data (e.g., shares, cost basis, current value)
- TRANSACTION: Metrics that track transaction-level data (e.g., fees, exchange rates)
- PORTFOLIO: Metrics that track portfolio-level data (e.g., total value, cash balance)

Computed metrics use the following sources:
- shares: Total shares calculation
- avg_price: Average purchase price
- cost_basis: Total cost basis
- current_value: Current position value
- position_gain: Position gain/loss percentage
- total_value: Total portfolio value
- cash_balance: Portfolio cash balance
- portfolio_return: Portfolio return calculation
- transaction_impact: Transaction impact calculation
- fee_percentage: Transaction fee percentage

Tags allow users to organize metrics into custom categories (e.g., "Fundamental", "Technical", "Risk") while maintaining the core structure based on scope_type.

### **Metric Values Table**

| Field       | Type      | Required | Description                      |
|-------------|-----------|----------|----------------------------------|
| value_id    | UUID      | Yes      | Primary identifier               |
| position    | UUID      | No       | Related position (conditional)   |
| portfolio   | UUID      | No       | Related portfolio (conditional)  |
| transaction | UUID      | No       | Related transaction (conditional)|
| metric_type | UUID      | Yes      | Reference to metric type         |
| date        | Date      | Yes      | Date of the value                |
| value       | Decimal   | No       | The numeric value                |
| text_value  | Text      | No       | Text content for memo-type metrics|
| source      | String    | Yes      | Data source or 'USER' for manual |
| confidence  | Decimal   | No       | Confidence score (0-1)           |
| is_forecast | Boolean   | Yes      | Actual or forecasted             |
| scenario    | Enum      | No       | NULL, BASE, BULL, BEAR           |
| notes       | Text      | No       | Any relevant notes               |
| created_at  | Timestamp | Yes      | Creation timestamp               |
| updated_at  | Timestamp | Yes      | Last update timestamp            |

**Important Notes:**
1. Only one of position, portfolio, or transaction can be set, based on the metric_type's scope_type
2. For memo-type metrics, text_value is used instead of value
3. Computed metrics are automatically calculated based on their computation_source
4. The source field indicates if the value was manually entered ('USER') or computed ('COMPUTED')

## **Position Analytics Table**

|Field|Type|Required|Description|
|---|---|---|---|
|analytics_id|UUID|Yes|Primary identifier for the analytic|
|position_id|UUID|Yes|Reference to position|
|analytic_type|Enum|Yes|Type of derived value (e.g., ALLOCATION_PERCENTAGE, INTRINSIC_VALUE, CURRENT_VALUE)|
|value|Decimal|Yes|The calculated value|
|calculation_method|String|No|Methodology used for calculation (e.g., P/E_RATIO, DCF, MARKET_PRICE)|
|date|Date|Yes|Date the analytic is relevant|
|calculated_at|Timestamp|Yes|Time when the analytic was calculated|

## Market Data Models

### **Security Table**

| Field          | Type       | Required | Description                           |
|----------------|------------|----------|---------------------------------------|
| id             | UUID       | Yes      | Primary identifier                    |
| symbol         | String     | Yes      | Ticker symbol (e.g., AAPL)            |
| name           | String     | Yes      | Company/security name                 |
| security_type  | Enum       | Yes      | STOCK, ETF, MUTUAL_FUND, etc.         |
| exchange       | String     | No       | Exchange where traded                 |
| currency       | String     | Yes      | Trading currency (e.g., USD)          |
| created_at     | Timestamp  | Yes      | Record creation time                  |
| updated_at     | Timestamp  | Yes      | Last update time                      |
| active         | Boolean    | Yes      | Whether security is active            |

### **PriceData Table**

| Field          | Type       | Required | Description                           |
|----------------|------------|----------|---------------------------------------|
| id             | UUID       | Yes      | Primary identifier                    |
| security       | ForeignKey | Yes      | Reference to Security                 |
| date           | Date       | Yes      | Date of the price data                |
| open           | Decimal    | Yes      | Opening price                         |
| high           | Decimal    | Yes      | Highest price of day                  |
| low            | Decimal    | Yes      | Lowest price of day                   |
| close          | Decimal    | Yes      | Closing price                         |
| adj_close      | Decimal    | Yes      | Adjusted closing price                |
| volume         | Integer    | Yes      | Trading volume                        |
| source         | String     | Yes      | Data source (e.g., "yahoo")           |
| created_at     | Timestamp  | Yes      | Record creation time                  |
| updated_at     | Timestamp  | Yes      | Last update time                      |

### **MarketDataSettings Table**

| Field            | Type       | Required | Description                           |
|------------------|------------|----------|---------------------------------------|
| id               | Integer    | Yes      | Primary key (always 1 - singleton)    |
| updates_enabled  | Boolean    | Yes      | Whether market data updates are enabled|
| last_modified    | Timestamp  | Yes      | Last modification time                |

## Key Relationships

1. User → Portfolio (1:M)
2. Portfolio → Position (1:M)
3. Position → Transaction (1:M)
4. Position → Position Analytics (1:1)
5. Portfolio → Portfolio Snapshot (1:M)
6. Position → Metric Values (1:M)
7. Metric Type → Metric Values (1:M)

## Inter-Model Relationships

### Position → Security

Positions in the portfolio app reference securities from the market_data app by ticker:

```python
# In portfolio/models.py
class Position(models.Model):
    # ...existing fields...
    ticker = models.CharField(max_length=10)  # Used to reference securities
    # Note: No direct foreign key to Security
```

This relationship:
- Links portfolio positions to market securities via ticker symbol
- Allows for flexibility in referencing securities that might not exist in the database yet
- Enables the market_data service to look up or create securities on demand

The actual connection is made through the MarketDataService:

```python
# In market_data/services.py
def sync_price_with_metrics(position):
    # Get security by ticker since Position doesn't have a direct security field
    security = MarketDataService.get_or_create_security(position.ticker)
    # ...get price data and update metrics...
```

### MetricValue → Security (Indirect)

Our implementation stores market prices as metrics rather than direct attributes:

```python
# Market Price stored as a metric value
metric_value = MetricValue.objects.update_or_create(
    position=position,
    metric_type=market_price_metric,
    date=price_date,
    defaults={
        'value': latest_price['price'],
        'source': latest_price['source'],
        'is_forecast': False
    }
)
```

This design:
- Maintains consistent treatment of all financial data as metrics
- Preserves price history automatically through the metrics system
- Enables the metrics computation system to use latest market data

## Data Access Patterns

### Global Context Data
The application uses Django context processors to make certain data globally available:

1. **Metric Types**
   - **Access Pattern**: Global template access via context processor
   - **Source**: MetricType model
   - **Organization**: Grouped by category
   - **Usage**: Available in all authenticated templates as `metrics_by_category`
   ```python
   {
       'Market Data': [MetricType objects],
       'Fundamental': [MetricType objects],
       'Technical': [MetricType objects],
       'Position': [MetricType objects]
   }
   ```

### Common Queries

1. **Position Metrics**
   ```python
   MetricValue.objects.filter(
       position=position,
       metric_type=metric_type
   ).order_by('-date', '-created_at')
   ```

2. **Active Positions**
   ```python
   Position.objects.filter(
       portfolio=portfolio,
       is_active=True
   )
   ```

3. **Position Transactions**
   ```python
   Transaction.objects.filter(
       position=position
   ).order_by('-date', '-created_at')
   ```

## Related Documentation
- [Templates](templates.md) - Template structure and components
- [Design Document](Design%20Document.md) - Application design and features