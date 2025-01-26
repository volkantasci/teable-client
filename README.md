# 🔌 Teable Client Library

A professional Python client library for interacting with the Teable API. This library provides an object-oriented interface for managing tables, records, fields, and views in Teable.

For full documentation, please visit: https://volkantasci.github.io/teable-client-docs/

## ✨ Features

- **Complete API Coverage** 🌐
  * Full Teable API support with an intuitive object-oriented interface
  * Comprehensive field type support with validation
  * Dashboard and plugin management
  * Data aggregation and analytics
  * User authentication and profile management
  * File attachment handling
  * Selection and range operations

- **Data Management** 💾
  * Efficient batch operations for creating, updating, and deleting records
  * Advanced querying capabilities with a fluent query builder
  * Field calculation planning and conversion
  * Table and view management
  * Record selection and manipulation

- **Performance & Reliability** ⚡
  * Automatic rate limiting and retry handling
  * Resource caching for improved performance
  * Connection pooling and management
  * Error handling and validation

- **Developer Experience** 👨‍💻
  * Type hints for better IDE support
  * Detailed documentation and examples
  * Comprehensive test coverage
  * Professional logging and debugging

## 📦 Installation

You can install the package using pip:

```bash
pip install teable-client==1.1.1  # Recommended stable version with improved search functionality
```

Or for the latest version:

```bash
pip install teable-client
```

## 🔄 Recent Changes

### Version 1.1.1
- Improved search functionality with better parameter handling
- Fixed issues with record query operations
- Added test utilities for better test organization
- Improved error handling in HTTP client

## 🛠️ Manager Classes

The Teable client provides several specialized manager classes for different aspects of the API:

- **TableManager**: Handle table operations, metadata, and structure
- **FieldManager**: Manage field definitions, types, and calculations
- **RecordManager**: Create, update, and delete records
- **ViewManager**: Configure and manage table views
- **DashboardManager**: Create and manage dashboards and widgets
- **AggregationManager**: Perform data aggregation and analytics
- **SelectionManager**: Handle table selection and range operations
- **AttachmentManager**: Manage file uploads and attachments
- **AuthManager**: Handle user authentication and profile management

## 🚀 Quick Start

```python
from teable import TeableClient, TeableConfig

# Initialize the client
config = TeableConfig(
    api_url="https://your-teable-instance.com/api",
    api_key="your-api-key"
)
client = TeableClient(config)

# Get a table
table = client.get_table("table_id")

# Create a record
record = table.create_record({
    "name": "John Doe",
    "email": "john@example.com",
    "age": 30
})

# Query records
query = table.query()\
    .filter("age", ">", 25)\
    .sort("name")\
    .paginate(take=10)
    
records = table.get_records(query)

# Batch create records
records_data = [
    {"name": "Alice", "age": 28},
    {"name": "Bob", "age": 32}
]
batch_result = table.batch_create_records(records_data)
print(f"Created {batch_result.success_count} records")
```

## 📚 Advanced Usage

### 📧 Working with Invitations

```python
# Accept an invitation link
result = client.accept_invitation_link(
    invitation_code="code123",
    invitation_id="inv123"
)
print(f"Space ID: {result['spaceId']}")
print(f"Base ID: {result['baseId']}")
```

### 🔗 Database Connections

```python
# Create a database connection
connection = client.create_db_connection(base_id="base123")
print(f"Connection URL: {connection['url']}")

# Get connection info
info = client.get_db_connection(base_id="base123")
print(f"Current connections: {info['connection']['current']}")
print(f"Max connections: {info['connection']['max']}")

# Delete connection
client.delete_db_connection(base_id="base123")
```

### 📊 Working with Dashboards

```python
# Create a dashboard
dashboard = client.dashboards.create_dashboard(
    name="Sales Overview",
    description="Key sales metrics and KPIs"
)

# Add a widget
widget = dashboard.add_widget({
    "type": "chart",
    "name": "Monthly Sales",
    "config": {
        "chartType": "bar",
        "dataSource": {
            "tableId": "table_id",
            "aggregation": "sum",
            "field": "amount"
        }
    }
})

# Get dashboard data
data = dashboard.get_data()
```

### 📈 Data Aggregation

```python
# Get aggregated data
result = client.aggregation.get_aggregation(
    table_id="table_id",
    group_by=["category"],
    metrics=[
        {"field": "amount", "function": "sum"},
        {"field": "quantity", "function": "avg"}
    ]
)

# Get calendar view
calendar = client.aggregation.get_calendar_daily_collection(
    table_id="table_id",
    date_field="due_date"
)

# Search and count
count = client.aggregation.get_search_count(
    table_id="table_id",
    search_text="urgent"
)
```

### 🏷️ Working with Fields

```python
from teable import FieldType, Field

# Get table fields
fields = table.fields

# Access field properties
for field in fields:
    print(f"{field.name} ({field.field_type})")
    if field.is_required:
        print("  Required field")
    if field.is_primary:
        print("  Primary field")

# Validate field values
field = table.get_field("field_id")
try:
    field.validate_value(some_value)
except ValidationError as e:
    print(f"Invalid value: {e}")
```

[Rest of the documentation continues with similar formatting...]

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
