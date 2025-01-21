# Teable Client Library

A professional Python client library for interacting with the Teable API. This library provides an object-oriented interface for managing tables, records, fields, and views in Teable.

## Features

- Full Teable API coverage with an intuitive object-oriented interface
- Comprehensive field type support with validation
- Efficient batch operations for creating, updating, and deleting records
- Advanced querying capabilities with a fluent query builder
- Automatic rate limiting and retry handling
- Resource caching for improved performance
- Type hints for better IDE support
- Detailed documentation and examples

## Installation

You can install the package using pip:

```bash
pip install teable-client
```

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
