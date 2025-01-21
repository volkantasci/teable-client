# Teable Client Library

A professional Python client library for interacting with the Teable API. This library provides an object-oriented interface for managing tables, records, fields, and views in Teable.

## Features

- **Complete API Coverage**
  * Full Teable API support with an intuitive object-oriented interface
  * Comprehensive field type support with validation
  * Dashboard and plugin management
  * Data aggregation and analytics
  * User authentication and profile management
  * File attachment handling
  * Selection and range operations

- **Data Management**
  * Efficient batch operations for creating, updating, and deleting records
  * Advanced querying capabilities with a fluent query builder
  * Field calculation planning and conversion
  * Table and view management
  * Record selection and manipulation

- **Performance & Reliability**
  * Automatic rate limiting and retry handling
  * Resource caching for improved performance
  * Connection pooling and management
  * Error handling and validation

- **Developer Experience**
  * Type hints for better IDE support
  * Detailed documentation and examples
  * Comprehensive test coverage
  * Professional logging and debugging

## Installation

You can install the package using pip:

```bash
pip install teable-client
```

## Manager Classes

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

## Quick Start

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

## Advanced Usage

### Working with Invitations

```python
# Accept an invitation link
result = client.accept_invitation_link(
    invitation_code="code123",
    invitation_id="inv123"
)
print(f"Space ID: {result['spaceId']}")
print(f"Base ID: {result['baseId']}")
```

### Database Connections

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

### Working with Dashboards

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

### Data Aggregation

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

### Working with Fields

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

### Selection Operations

```python
# Get selection range
selection = client.selection.get_selection_range_to_id(
    table_id="table_id",
    ranges="[[0, 0], [1, 1]]",
    return_type="all"
)

# Copy selection
copy_result = client.selection.get_selection_copy(
    table_id="table_id",
    ranges="[[0, 0], [1, 1]]"
)

# Paste selection
paste_result = client.selection.paste_selection(
    table_id="table_id",
    ranges=[[0, 0], [1, 1]],
    content="Pasted content"
)
```

### File Attachments

```python
# Upload attachment
signature = client.attachments.get_attachment_signature(
    content_type="image/png",
    content_length=1024,
    attachment_type=1
)

client.attachments.upload_attachment_with_token(
    token=signature["token"],
    file_data=image_bytes
)

# Get attachment info
info = client.attachments.notify_attachment(token="attachment_token")
print(f"File URL: {info['url']}")

# Download attachment
data = client.attachments.get_attachment(token="attachment_token")
```

### User Management

```python
# Get user info
user = client.auth.get_user_info()
print(f"User: {user.name} ({user.email})")

# Update profile
client.auth.update_user_name("New Name")
client.auth.update_user_notify_meta(email=True)

# Upload avatar
with open("avatar.png", "rb") as f:
    client.auth.update_user_avatar(f.read())
```

### Using Views

```python
# Get table views
views = table.views

# Get records from a specific view
view = table.get_view("view_id")
query = view.create_query().paginate(take=20)
records = table.get_records(query)
```

### Advanced Querying

```python
from teable import FilterOperator, SortDirection

# Complex query with multiple conditions
query = table.query()\
    .filter("status", FilterOperator.EQUALS, "active")\
    .filter("age", FilterOperator.GREATER_THAN, 25)\
    .filter("tags", FilterOperator.CONTAINS, "important")\
    .sort("created_time", SortDirection.DESCENDING)\
    .sort("priority")\
    .search("urgent", field="title")\
    .paginate(take=50, skip=100)

records = table.get_records(query)
```

### Batch Operations

```python
# Batch create
records_data = [
    {"name": "Alice", "department": "Engineering"},
    {"name": "Bob", "department": "Marketing"}
]
batch_result = table.batch_create_records(records_data)

print(f"Successfully created: {batch_result.success_count}")
if batch_result.failed:
    print("Failed operations:")
    for failure in batch_result.failed:
        print(f"  {failure}")

# Batch update
updates = [
    {"id": "rec1", "fields": {"status": "completed"}},
    {"id": "rec2", "fields": {"status": "completed"}}
]
table.batch_update_records(updates)

# Batch delete
record_ids = ["rec1", "rec2", "rec3"]
table.batch_delete_records(record_ids)
```

### Error Handling

```python
from teable import (
    TeableError,
    APIError,
    ValidationError,
    ResourceNotFoundError
)

try:
    record = table.get_record("invalid_id")
except ResourceNotFoundError as e:
    print(f"Record not found: {e}")
except ValidationError as e:
    print(f"Validation error: {e}")
except APIError as e:
    print(f"API error {e.status_code}: {e}")
except TeableError as e:
    print(f"Other error: {e}")
```

## API Reference

### TableManager

```python
class TableManager:
    def get_table(self, table_id: str) -> Table
    def get_tables(self) -> List[Table]
    def create_table(self, base_id: str, name: str, ...) -> Table
    def delete_table(self, base_id: str, table_id: str) -> bool
    def update_table_name(self, base_id: str, table_id: str, name: str) -> bool
    def update_table_icon(self, base_id: str, table_id: str, icon: str) -> bool
    def update_table_description(self, base_id: str, table_id: str, description: str) -> bool
```

### DashboardManager

```python
class DashboardManager:
    def create_dashboard(self, name: str, description: str = None) -> Dashboard
    def get_dashboard(self, dashboard_id: str) -> Dashboard
    def update_dashboard(self, dashboard_id: str, ...) -> Dashboard
    def delete_dashboard(self, dashboard_id: str) -> bool
    def add_widget(self, dashboard_id: str, widget_config: Dict) -> Widget
```

### AggregationManager

```python
class AggregationManager:
    def get_aggregation(self, table_id: str, ...) -> Dict[str, Any]
    def get_row_count(self, table_id: str, ...) -> int
    def get_group_points(self, table_id: str, ...) -> List[Dict]
    def get_calendar_daily_collection(self, table_id: str, ...) -> Dict
    def get_search_count(self, table_id: str, ...) -> int
```

### SelectionManager

```python
class SelectionManager:
    def get_selection_range_to_id(self, table_id: str, ...) -> SelectionRange
    def clear_selection(self, table_id: str, ...) -> bool
    def get_selection_copy(self, table_id: str, ...) -> Dict[str, Any]
    def paste_selection(self, table_id: str, ...) -> Dict[str, List[List[int]]]
    def delete_selection(self, table_id: str, ...) -> Dict[str, List[str]]
```

### AttachmentManager

```python
class AttachmentManager:
    def upload_attachment(self, table_id: str, ...) -> Dict[str, Any]
    def notify_attachment(self, token: str, ...) -> Dict[str, Any]
    def get_attachment(self, token: str, ...) -> bytes
    def get_attachment_signature(self, content_type: str, ...) -> Dict[str, Any]
```

### AuthManager

```python
class AuthManager:
    def get_user_info(self) -> User
    def update_user_name(self, name: str) -> bool
    def update_user_avatar(self, avatar_data: bytes) -> bool
    def update_user_notify_meta(self, email: bool) -> bool
    def signin(self, email: str, password: str) -> User
    def signout(self) -> bool
```

## Configuration Options

The `TeableConfig` class supports various options to customize the client behavior:

```python
config = TeableConfig(
    api_url="https://your-teable-instance.com/api",
    api_key="your-api-key",
    timeout=30.0,          # Request timeout in seconds
    max_retries=3,         # Maximum number of retry attempts
    retry_delay=1.0,       # Delay between retries in seconds
    default_table_id=None, # Default table ID for operations
    default_view_id=None   # Default view ID for operations
)
```

## Development

To set up the development environment:

1. Clone the repository
2. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```
3. Run tests:
   ```bash
   pytest
   ```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
