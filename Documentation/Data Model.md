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
| category    | Enum    | Yes      | MARKET_DATA, FUNDAMENTAL, TECHNICAL   |
| data_type   | Enum    | Yes      | PRICE, RATIO, VOLUME, PERCENTAGE     |
| description | Text    | No       | Description of the metric             |
| is_system   | Boolean | Yes      | System or user-defined metric         |

### **Metric Values Table**

| Field       | Type      | Required | Description                      |
|-------------|-----------|----------|----------------------------------|
| value_id    | UUID      | Yes      | Primary identifier               |
| position_id | UUID      | Yes      | Related position                 |
| metric_id   | UUID      | Yes      | Reference to metric type         |
| date        | Date      | Yes      | Date of the value                |
| value       | Decimal   | Yes      | The actual value                 |
| source      | String    | Yes      | Data source or 'USER' for forecasts|
| confidence  | Decimal   | No       | Confidence score (0-1)           |
| is_forecast | Boolean   | Yes      | Actual or forecasted             |
| scenario    | Enum      | No       | NULL, BASE, BULL, BEAR           |
| notes       | Text      | No       | Any relevant notes               |

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


## Key Relationships

1. User → Portfolio (1:M)
2. Portfolio → Position (1:M)
3. Position → Transaction (1:M)
4. Position → Position Analytics (1:1)
5. Portfolio → Portfolio Snapshot (1:M)
6. Position → Metric Values (1:M)
7. Metric Type → Metric Values (1:M)

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