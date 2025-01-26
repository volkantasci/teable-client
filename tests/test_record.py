"""Test suite for Record operations."""
import json
import time
import pytest
from datetime import datetime
from teable.models.record import Record, RecordBatch, RecordStatus
from teable.exceptions import ValidationError, APIError

from .utils import wait_for_records

def write_debug(msg):
    """Write debug message."""
    print(f"\n{datetime.now()}: [RECORD TEST] {msg}")

@pytest.fixture(scope='function')
def test_space(authenticated_client):
    """Create a test space for record operations."""
    # Create space
    space = authenticated_client.spaces.create_space(name="Record Test Space")
    yield space
    # Cleanup
    authenticated_client.spaces.permanently_delete_space(space.space_id)

@pytest.fixture(scope='function')
def test_base(test_space):
    """Create a test base for record operations."""
    # Create base
    base = test_space.create_base(name="Record Test Base")
    yield base
    # Cleanup handled by space deletion

def test_record_crud_operations(authenticated_client, test_space, test_base):
    """Test record creation, reading, updating, and deletion."""
    write_debug("Starting CRUD test")
    write_debug(f"Client config: {authenticated_client._http.config.__dict__}")
    write_debug(f"Client headers: {authenticated_client._http.session.headers}")
    try:
        # Create a table with fields
        write_debug("Creating table")
        table = authenticated_client.tables.create_table(
            base_id=test_base.base_id,
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
        write_debug(f"Created table: {table.table_id}")
        
        # Create a record
        write_debug("Creating record")
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
        
        write_debug(f"Created record: {record.record_id}")
        
        # Get record
        write_debug("Fetching record")
        fetched_record = Record.from_api_response(
            authenticated_client.records.get_record(table.table_id, record.record_id)
        )
        assert fetched_record.record_id == record.record_id
        assert fetched_record.fields == record.fields
        
        write_debug("Record fetched successfully")
        
        # Update record
        write_debug("Updating record")
        updated_data = {
            "Description": "Updated Description",
            "Count": 43
        }
        updated_record = Record.from_api_response(
            authenticated_client.records.update_record(table.table_id, record.record_id, updated_data)
        )
        assert updated_record.fields["Description"] == "Updated Description"
        assert updated_record.fields["Count"] == 43
        
        write_debug("Record updated successfully")
        
        # Delete record
        write_debug("Deleting record")
        assert authenticated_client.records.delete_record(table.table_id, record.record_id)
        write_debug("Record deleted successfully")
        
        # Clean up
        write_debug("Cleaning up")
        test_base.delete()
        write_debug("CRUD test completed successfully")
        
    except Exception as e:
        write_debug(f"Error in CRUD test: {str(e)}")
        raise

def test_record_batch_operations(authenticated_client, test_space, test_base):
    """Test batch record operations."""
    
    # Create a table
    table = authenticated_client.tables.create_table(
        base_id=test_base.base_id,
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
    
    # Get records and wait for them to be available
    records = wait_for_records(authenticated_client, table.table_id, 3)
    assert len(records) == 3
    
    # Batch update records
    updates = [
        {
            "id": record["id"],
            "fields": {"Value": record["fields"]["Value"] * 2}
        }
        for record in records
    ]
    updated_records = [
        Record.from_api_response(r)
        for r in authenticated_client.records.batch_update_records(table.table_id, updates)
    ]
    assert len(updated_records) == 3
    assert all(r.fields["Value"] == i * 2 for i, r in enumerate(updated_records, 1))
    
    # Batch delete records
    record_ids = [record["id"] for record in records]
    assert authenticated_client.records.batch_delete_records(table.table_id, record_ids)
    
    # Verify deletion with retries
    remaining_records = wait_for_records(authenticated_client, table.table_id, 0)
    assert len(remaining_records) == 0
    
    # Clean up
    test_base.delete()

def test_record_query_operations(authenticated_client, test_space, test_base):
    """Test record query operations."""
    
    # Create a table with test data
    table = authenticated_client.tables.create_table(
        base_id=test_base.base_id,
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
    
    # Add test records and wait for them to be available
    records_data = [
        {"Name": "Item 1", "Category": "A", "Value": 10},
        {"Name": "Item 2", "Category": "A", "Value": 20},
        {"Name": "Item 3", "Category": "B", "Value": 30},
        {"Name": "Item 4", "Category": "B", "Value": 40}
    ]
    batch_result = authenticated_client.records.batch_create_records(table.table_id, records_data)
    assert batch_result.success_count == 4
    
    # Wait for records to be indexed
    records = wait_for_records(authenticated_client, table.table_id, 4)
    assert len(records) == 4
    
    # Get field IDs
    fields = authenticated_client.fields.get_table_fields(table.table_id)
    category_field = next(f for f in fields if f.name == "Category")
    
    # Test filtering
    filter_params = {
            "filterSet": [
                {
                    "operator": "is",
                    "fieldId": category_field.field_id,
                    "value": "A"
                }
            ],
            "conjunction": "and"
    }
    filtered_records = wait_for_records(
        authenticated_client,
        table.table_id,
        2,  # Expect 2 records with Category "A"
        filter=filter_params
    )
    assert len(filtered_records) == 2
    assert all(r["fields"]["Category"] == "A" for r in filtered_records)
    
    # Test search
    # Get field IDs
    name_field = next(f for f in fields if f.name == "Name")
    search_params = {
        "search": [{
            "value": "Item 1",
            "field": name_field.field_id,  # Use field ID instead of name
            "exact": True
        }]
    }
    searched_records = wait_for_records(
        authenticated_client,
        table.table_id,
        1,  # Expect 1 record matching search
        **search_params
    )
    assert len(searched_records) == 1
    assert searched_records[0]["fields"]["Name"] == "Item 1"
    
    # Test pagination - skip first 3 default empty records
    pagination_params = {
        "skip": 3,  # Skip the 3 default empty records
        "take": 2   # Take 2 records from our actual data
    }
    paginated_records = wait_for_records(
        authenticated_client,
        table.table_id,
        2,  # Expect 2 records
        **pagination_params
    )
    assert len(paginated_records) == 2
    # Verify we got the expected records (first two of our actual data)
    assert paginated_records[0]["fields"]["Name"] == "Item 1"
    assert paginated_records[1]["fields"]["Name"] == "Item 2"
    
    # Clean up
    test_base.delete()

def test_record_status_and_history(authenticated_client, test_space, test_base):
    """Test record status and history operations."""
    
    # Create a table
    table = authenticated_client.tables.create_table(
        base_id=test_base.base_id,
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
    test_base.delete()

def test_record_validation(authenticated_client, test_space, test_base):
    """Test record validation rules."""
    
    # Create a table with required field
    table = authenticated_client.tables.create_table(
        base_id=test_base.base_id,
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
    
    # Test invalid field name
    with pytest.raises(APIError):  # API should return an error for invalid field
        authenticated_client.records.create_record(
            table.table_id,
            {"Required Field": "value", "Invalid Field": "value"}
        )
    
    # Test batch validation
    with pytest.raises(ValidationError):
        authenticated_client.records.batch_create_records(table.table_id, [])  # Empty list
    
    with pytest.raises(ValidationError):
        authenticated_client.records.batch_create_records(
            table.table_id,
            [{"Required Field": str(i)} for i in range(2001)]  # Too many records
        )
    
    # Clean up
    test_base.delete()

def test_record_field_operations(authenticated_client, test_space, test_base):
    """Test record field value operations."""
    
    # Create a table with different field types
    table = authenticated_client.tables.create_table(
        base_id=test_base.base_id,
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
    test_base.delete()
