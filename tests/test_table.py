"""Test suite for Table operations."""
import json
import pytest
from teable.models.table import Table
from teable.exceptions import ValidationError
from .utils import wait_for_records

def test_table_crud_operations(authenticated_client):
    """Test table creation, reading, updating, and deletion."""
    # Create a space first
    space = authenticated_client.spaces.create_space(name="Table Test Space")
    
    # Create a base
    base = space.create_base(name="Table Test Base")
    
    # Create a table
    table = authenticated_client.tables.create_table(
        base_id=base.base_id,
        name="Test Table",
        db_table_name="testtable",
        description="Test table description"
    )
    
    assert isinstance(table, Table)
    assert table.name == "Test Table"
    assert table.description == "Test table description"
    
    # Update table name
    authenticated_client.tables.update_table_name(base.base_id, table.table_id, "Updated Table")
    updated_table = authenticated_client.tables.get_table(table.table_id, base_id=base.base_id)
    assert updated_table.name == "Updated Table"
    
    # Update description
    authenticated_client.tables.update_table_description(
        base.base_id,
        table.table_id,
        "Updated description"
    )
    updated_table = authenticated_client.tables.get_table(table.table_id, base_id=base.base_id)
    assert updated_table.description == "Updated description"
    
    # Delete table
    assert authenticated_client.tables.delete_table(base.base_id, table.table_id)
    
    # Clean up
    base.delete()
    authenticated_client.spaces.permanently_delete_space(space.space_id)

def test_table_creation_validation(authenticated_client):
    """Test table creation validation rules."""
    # Create a space first
    space = authenticated_client.spaces.create_space(name="Table Validation Space")
    
    # Create a base
    base = space.create_base(name="Table Validation Test Base")
    
    # Test invalid db_table_name
    with pytest.raises(ValueError):
        authenticated_client.tables.create_table(
            base_id=base.base_id,
            name="Invalid Table",
            db_table_name="1invalid_name"  # Must start with letter
        )
    
    with pytest.raises(ValueError):
        authenticated_client.tables.create_table(
            base_id=base.base_id,
            name="Invalid Table",
            db_table_name="a" * 64  # Too long
        )
    
    # Clean up
    base.delete()
    authenticated_client.spaces.permanently_delete_space(space.space_id)

def test_table_record_operations(authenticated_client):
    """Test table record operations."""
    # Create a space first
    space = authenticated_client.spaces.create_space(name="Record Test Space")
    
    # Create a base
    base = space.create_base(name="Record Test Base")
    
    # Create a table with fields
    table = authenticated_client.tables.create_table(
        base_id=base.base_id,
        name="Record Test Table",
        db_table_name="recordtest",
        fields=[
            {
                "name": "Name",
                "type": "singleLineText",
                "required": True
            },
            {
                "name": "Age",
                "type": "number",
                "precision": 0
            }
        ]
    )
    
    # Create a record
    record = table.create_record({
        "Name": "Test User",
        "Age": 25
    })
    assert record.fields["Name"] == "Test User"
    assert record.fields["Age"] == 25
    
    # Update record
    updated_record = authenticated_client.records.update_record(
        table.table_id,
        record.record_id,
        {"Age": 26}
    )
    assert updated_record["fields"]["Age"] == 26
    
    # Get record
    fetched_record = authenticated_client.records.get_record(table.table_id, record.record_id)
    assert fetched_record["fields"]["Age"] == 26
    
    # Delete record
    assert authenticated_client.records.delete_record(table.table_id, record.record_id)
    
    # Clean up
    base.delete()
    authenticated_client.spaces.permanently_delete_space(space.space_id)

def test_table_batch_operations(authenticated_client):
    """Test table batch record operations."""
    # Create a space first
    space = authenticated_client.spaces.create_space(name="Batch Test Space")
    
    # Create a base
    base = space.create_base(name="Batch Test Base")
    
    # Create a table
    table = authenticated_client.tables.create_table(
        base_id=base.base_id,
        name="Batch Test Table",
        db_table_name="batchtest",
        fields=[
            {
                "name": "Name",
                "type": "singleLineText"
            }
        ]
    )
    
    # Batch create records
    records_data = [
        {"fields": {"Name": "User 1"}},
        {"fields": {"Name": "User 2"}},
        {"fields": {"Name": "User 3"}}
    ]
    batch_result = table.batch_create_records(records_data, field_key_type="name")
    assert len(batch_result.successful) == 3
    
    # Get all records
    all_records = table.get_records(field_key_type="name")
    assert len(all_records) == 6  # 3 varsayılan + 3 yeni kayıt
    
    # Batch update records
    updates = [
        {
            "id": record.record_id,
            "fields": {"Name": f"Updated {record.fields.get('Name', '')}"}
        }
        for record in all_records
    ]
    updated_records = table.batch_update_records(updates)
    assert len(updated_records) == 6  # Tüm kayıtlar güncellendi
    assert all("Updated" in record.fields.get("Name", "") for record in updated_records)
    
    # Batch delete records
    record_ids = [record.record_id for record in all_records]
    assert table.batch_delete_records(record_ids)
    
    # Verify deletion
    remaining_records = table.get_records()
    assert len(remaining_records) == 0
    
    # Clean up
    base.delete()
    authenticated_client.spaces.permanently_delete_space(space.space_id)

def test_table_query_operations(authenticated_client):
    """Test table query operations."""
    # Create a space first
    space = authenticated_client.spaces.create_space(name="Query Test Space")
    
    # Create a base
    base = space.create_base(name="Query Test Base")
    
    # Create a table with test data
    table = authenticated_client.tables.create_table(
        base_id=base.base_id,
        name="Query Test Table",
        db_table_name="querytest",
        fields=[
            {
                "name": "Name",
                "type": "singleLineText"
            },
            {
                "name": "Age",
                "type": "number",
                "precision": 0
            }
        ]
    )
    
    # Add test records
    test_records = [
        {"fields": {"Name": "Alice", "Age": 25}},
        {"fields": {"Name": "Bob", "Age": 30}},
        {"fields": {"Name": "Charlie", "Age": 35}}
    ]
    table.batch_create_records(test_records, field_key_type="name")
    
    # Test various query parameters
    # Filter by field value
    filter_data = {
        "filterSet": [
            {
                "fieldId": "Age",
                "operator": "isGreaterEqual",
                "value": 30,
                "isSymbol": False
            }
        ],
        "conjunction": "and"
    }
    filtered_records = table.get_records(
        filter=json.dumps(filter_data),
        field_key_type="name"
    )
    assert len(filtered_records) == 2
    
    # Get field IDs for search
    fields = authenticated_client.fields.get_table_fields(table.table_id)
    name_field = next(f for f in fields if f.name == "Name")

    # Test search with field ID
    search_params = {
        "search": [{
            "value": "Alice",
            "field": name_field.field_id,
            "exact": True
        }],
        "field_key_type": "name"
    }
    searched_records = wait_for_records(
        authenticated_client,
        table.table_id,
        1,  # Expect 1 record matching search
        **search_params
    )
    assert len(searched_records) == 1
    assert searched_records[0]["fields"]["Name"] == "Alice"
    
    # Test pagination - skip first 3 default empty records
    paginated_records = table.get_records(
        skip=3,  # Skip the 3 default empty records
        take=2   # Take 2 records from our actual data
    )
    assert len(paginated_records) == 2
    assert paginated_records[0].fields["Name"] == "Alice"
    assert paginated_records[1].fields["Name"] == "Bob"
    
    # Clean up
    base.delete()
    authenticated_client.spaces.permanently_delete_space(space.space_id)

def test_table_field_operations(authenticated_client):
    """Test table field operations."""
    # Create a space first
    space = authenticated_client.spaces.create_space(name="Field Test Space")
    
    # Create a base
    base = space.create_base(name="Field Test Base")
    
    # Create a table with fields
    table = authenticated_client.tables.create_table(
        base_id=base.base_id,
        name="Field Test Table",
        db_table_name="fieldtest",
        fields=[
            {
                "name": "Name",
                "type": "singleLineText",
                "required": True
            }
        ]
    )
    
    # Get fields
    fields = table.fields
    assert len(fields) >= 1  # Should have at least the Name field
    
    # Verify field attributes
    name_field = next(f for f in fields if f.name == "Name")
    # API doesn't support required flag currently
    assert name_field.field_type == "singleLineText"
    
    # Clean up
    base.delete()
    authenticated_client.spaces.permanently_delete_space(space.space_id)

def test_table_view_operations(authenticated_client):
    """Test table view operations."""
    # Create a space first
    space = authenticated_client.spaces.create_space(name="View Test Space")
    
    # Create a base
    base = space.create_base(name="View Test Base")
    
    # Create a table with a view
    table = authenticated_client.tables.create_table(
        base_id=base.base_id,
        name="View Test Table",
        db_table_name="viewtest",
        fields=[{"name": "Name", "type": "singleLineText"}],
        views=[{
            "name": "Test View",
            "type": "grid"
        }]
    )
    
    # Get views
    views = table.views
    assert len(views) >= 1
    
    # Get default view ID
    default_view_id = authenticated_client.tables.get_table_default_view_id(
        base.base_id,
        table.table_id
    )
    assert default_view_id
    
    # Clean up
    base.delete()
    authenticated_client.spaces.permanently_delete_space(space.space_id)

def test_get_base_tables(authenticated_client):
    """Test getting all tables in a base."""
    # Create a space first
    space = authenticated_client.spaces.create_space(name="Tables Test Space")
    
    # Create a base
    base = space.create_base(name="Tables Test Base")
    
    # Create multiple tables
    table1 = authenticated_client.tables.create_table(
        base_id=base.base_id,
        name="Test Table 1",
        db_table_name="testtable1"
    )
    
    table2 = authenticated_client.tables.create_table(
        base_id=base.base_id,
        name="Test Table 2",
        db_table_name="testtable2"
    )
    
    # Get all tables in the base
    tables = base.get_tables()
    
    # Verify tables were retrieved
    assert len(tables) >= 2  # At least our 2 created tables
    table_names = [t.name for t in tables]
    assert "Test Table 1" in table_names
    assert "Test Table 2" in table_names
    
    # Clean up
    base.delete()
    authenticated_client.spaces.permanently_delete_space(space.space_id)

def test_get_existing_base_tables(authenticated_client):
    """Test getting tables from first existing base."""
    # Get first space
    spaces = authenticated_client.spaces.get_spaces()
    if not spaces:
        pytest.skip("No spaces available for testing")
    
    space = spaces[0]
    
    # Get first base
    bases = space.get_bases()
    if not bases:
        pytest.skip("No bases available for testing")
    
    base = bases[0]
    
    # Get all tables in the base
    tables = base.get_tables()
    
    # Print table names for visibility
    print("\nTables in first base:")
    for table in tables:
        print(f"- {table.name}")
    
    # Just verify we can get tables
    assert isinstance(tables, list)

def test_table_permissions(authenticated_client):
    """Test table permission operations."""
    # Create a space first
    space = authenticated_client.spaces.create_space(name="Permission Test Space")
    
    # Create a base
    base = space.create_base(name="Permission Test Base")
    
    # Create a table
    table = authenticated_client.tables.create_table(
        base_id=base.base_id,
        name="Permission Test Table",
        db_table_name="permissiontest"
    )
    
    # Get permissions
    permissions = authenticated_client.tables.get_table_permission(
        base.base_id,
        table.table_id
    )
    
    # Verify permission structure
    assert "table" in permissions
    assert "view" in permissions
    assert "record" in permissions
    assert "field" in permissions
    
    # Clean up
    base.delete()
    authenticated_client.spaces.permanently_delete_space(space.space_id)
