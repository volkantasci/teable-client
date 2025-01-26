"""Test suite for Record operations."""
import json
import pytest
from datetime import datetime
from teable.models.record import Record, RecordBatch, RecordStatus
from teable.exceptions import ValidationError

@pytest.fixture
def test_space(authenticated_client):
    """Create a test space for record tests."""
    spaces = authenticated_client.spaces.get_spaces()
    space = spaces[0]
    return space

def test_record_crud_operations(authenticated_client, test_space):
    """Test record creation, reading, updating, and deletion."""
    # Create a base with a table first
    space = test_space
    base = space.create_base(name="Record Test Base")
    
    # Create a table with fields
    table = authenticated_client.tables.create_table(
        base_id=base.base_id,
        name="Record Test Table",
        db_table_name="recordtest",
        fields=[
            {
                "name": "Title",
                "type": "singleLineText",
                "required": True
            },
            {
                "name": "Description",
                "type": "singleLineText"
            },
            {
                "name": "Count",
                "type": "number",
                "precision": 0
            }
        ]
    )
    
    # Create a record
    record_data = {
        "Title": "Test Record",
        "Description": "Test Description",
        "Count": 42
    }
    record = Record.from_api_response(
        authenticated_client.records.create_record(table.table_id, record_data)
    )
    
    assert isinstance(record, Record)
    assert record.record_id
    assert record.fields["Title"] == "Test Record"
    assert record.fields["Count"] == 42
    
    # Get record
    fetched_record = Record.from_api_response(
        authenticated_client.records.get_record(table.table_id, record.record_id)
    )
    assert fetched_record.record_id == record.record_id
    assert fetched_record.fields == record.fields
    
    # Update record
    updated_data = {
        "Description": "Updated Description",
        "Count": 43
    }
    updated_record = Record.from_api_response(
        authenticated_client.records.update_record(table.table_id, record.record_id, updated_data)
    )
    assert updated_record.fields["Description"] == "Updated Description"
    assert updated_record.fields["Count"] == 43
    
    # Delete record
    assert authenticated_client.records.delete_record(table.table_id, record.record_id)
    
    # Clean up
    base.delete()

def test_record_batch_operations(authenticated_client, test_space):
    """Test batch record operations."""
    space = test_space
    base = space.create_base(name="Batch Record Test Base")
    
    # Create a table
    table = authenticated_client.tables.create_table(
        base_id=base.base_id,
        name="Batch Record Test Table",
        db_table_name="batchrecordtest",
        fields=[
            {
                "name": "Name",
                "type": "singleLineText"
            },
            {
                "name": "Value",
                "type": "number"
            }
        ]
    )
    
    # Batch create records
    records_data = [
        {"Name": "Record 1", "Value": 1},
        {"Name": "Record 2", "Value": 2},
        {"Name": "Record 3", "Value": 3}
    ]
    batch_result = authenticated_client.records.batch_create_records(table.table_id, records_data)
    assert isinstance(batch_result, RecordBatch)
    assert batch_result.success_count == 3
    assert batch_result.failure_count == 0
    assert len(batch_result.successful) == 3
    
    # Get all records (including 3 default empty records)
    all_records = [
        Record.from_api_response(r)
        for r in authenticated_client.records.get_records(table.table_id)
    ]
    # Filter out empty records (default records have empty fields)
    non_empty_records = [r for r in all_records if r.fields]
    assert len(non_empty_records) == 3
    
    # Batch update records (only update non-empty records)
    updates = [
        {
            "id": record.record_id,
            "fields": {"Value": record.fields["Value"] * 2}
        }
        for record in non_empty_records  # Use non_empty_records instead of all_records
    ]
    updated_records = [
        Record.from_api_response(r)
        for r in authenticated_client.records.batch_update_records(table.table_id, updates)
    ]
    assert len(updated_records) == 3
    assert all(r.fields["Value"] == i * 2 for i, r in enumerate(updated_records, 1))
    
    # Batch delete records (only delete non-empty records)
    record_ids = [record.record_id for record in non_empty_records]  # Only delete non-empty records
    assert authenticated_client.records.batch_delete_records(table.table_id, record_ids)
    
    # Wait a moment for deletion to complete
    import time
    time.sleep(1)
    
    # Verify deletion
    remaining_records = authenticated_client.records.get_records(table.table_id)
    assert len(remaining_records) == 0
    
    # Clean up
    base.delete()

def test_record_query_operations(authenticated_client, test_space):
    """Test record query operations."""
    space = test_space
    base = space.create_base(name="Record Query Test Base")
    
    # Create a table with test data
    table = authenticated_client.tables.create_table(
        base_id=base.base_id,
        name="Record Query Test Table",
        db_table_name="recordquerytest",
        fields=[
            {
                "name": "Name",
                "type": "singleLineText"
            },
            {
                "name": "Category",
                "type": "singleLineText"
            },
            {
                "name": "Value",
                "type": "number",
                "precision": 0
            }
        ]
    )
    
    # Add test records
    records_data = [
        {"Name": "Item 1", "Category": "A", "Value": 10},
        {"Name": "Item 2", "Category": "A", "Value": 20},
        {"Name": "Item 3", "Category": "B", "Value": 30},
        {"Name": "Item 4", "Category": "B", "Value": 40}
    ]
    authenticated_client.records.batch_create_records(table.table_id, records_data)
    
    # Get field IDs
    fields = authenticated_client.fields.get_table_fields(table.table_id)
    category_field = next(f for f in fields if f.name == "Category")
    
    # Test filtering
    filtered_records = authenticated_client.records.get_records(
        table.table_id,
        filter={
            "filterSet": [
                {
                    "operator": "is",
                    "fieldId": category_field.field_id,
                    "value": "A"
                }
            ],
            "conjunction": "and"
        }
    )
    # Filter out empty records (default records have empty fields)
    non_empty_records = [r for r in filtered_records if r["fields"]]
    assert len(non_empty_records) == 2
    assert all(r["fields"]["Category"] == "A" for r in non_empty_records)
    
    # Test search (using array format)
    searched_records = authenticated_client.records.get_records(
        table.table_id,
        search=[{"value": "Item 1"}]  # Keep as array since http client will handle it
    )
    assert len(searched_records) == 1
    assert searched_records[0]["fields"]["Name"] == "Item 1"
    
    # Test pagination
    paginated_records = authenticated_client.records.get_records(
        table.table_id,
        take=2,
        skip=1
    )
    assert len(paginated_records) == 2
    
    # Clean up
    base.delete()

def test_record_status_and_history(authenticated_client, test_space):
    """Test record status and history operations."""
    space = test_space
    base = space.create_base(name="Record Status Test Base")
    
    # Create a table
    table = authenticated_client.tables.create_table(
        base_id=base.base_id,
        name="Record Status Test Table",
        db_table_name="recordstatustest",
        fields=[{"name": "Name", "type": "singleLineText"}]
    )
    
    # Create a record
    record = Record.from_api_response(
        authenticated_client.records.create_record(table.table_id, {"Name": "Test Record"})
    )
    
    # Get record status
    status = authenticated_client.records.get_record_status(table.table_id, record.record_id)
    assert isinstance(status, RecordStatus)
    assert status.is_visible
    assert not status.is_deleted
    
    # Get record history
    history = authenticated_client.records.get_record_history(table.table_id, record.record_id)
    # A newly created record might not have history entries yet
    assert history.users is not None
    
    # Get table record history
    table_history = authenticated_client.records.get_table_record_history(table.table_id)
    # A new table might not have history entries yet
    assert table_history.users is not None
    
    # Clean up
    base.delete()

def test_record_validation(authenticated_client, test_space):
    """Test record validation rules."""
    space = test_space
    base = space.create_base(name="Record Validation Test Base")
    
    # Create a table with required field
    table = authenticated_client.tables.create_table(
        base_id=base.base_id,
        name="Record Validation Test Table",
        db_table_name="recordvalidationtest",
        fields=[
            {
                "name": "Required Field",
                "type": "singleLineText",
                "required": True
            }
        ]
    )
    
    # Test missing required field
    with pytest.raises(ValidationError):
        authenticated_client.records.create_record(table.table_id, {})
    
    try:
        # Test invalid field name
        with pytest.raises(ValidationError):
            authenticated_client.records.create_record(table.table_id, {"Required Field": "value", "Invalid Field": "value"})
    except Exception as e:
        # If we get a different error, print it for debugging
        print(f"Unexpected error: {str(e)}")
        raise
    
    # Test batch validation
    with pytest.raises(ValidationError):
        authenticated_client.records.batch_create_records(table.table_id, [])  # Empty list
    
    with pytest.raises(ValidationError):
        authenticated_client.records.batch_create_records(
            table.table_id,
            [{"Required Field": str(i)} for i in range(2001)]  # Too many records
        )
    
    # Clean up
    base.delete()

def test_record_field_operations(authenticated_client, test_space):
    """Test record field value operations."""
    space = test_space
    base = space.create_base(name="Record Field Test Base")
    
    # Create a table with different field types
    table = authenticated_client.tables.create_table(
        base_id=base.base_id,
        name="Record Field Test Table",
        db_table_name="recordfieldtest",
        fields=[
            {
                "name": "Text Field",
                "type": "singleLineText"
            },
            {
                "name": "Number Field",
                "type": "number",
                "precision": 0
            }
        ]
    )
    
    # Create a record
    record = Record.from_api_response(
        authenticated_client.records.create_record(
            table.table_id,
            {
                "Text Field": "Test Value",
                "Number Field": 42
            }
        )
    )
    
    # Test get_field_value
    assert record.get_field_value("Text Field") == "Test Value"
    assert record.get_field_value("Number Field") == 42
    
    # Test set_field_value
    record.set_field_value("Text Field", "New Value")
    assert record.fields["Text Field"] == "New Value"
    
    # Test invalid field access
    with pytest.raises(KeyError):
        record.get_field_value("Non-existent Field")
    
    # Clean up
    base.delete()
