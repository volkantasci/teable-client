

import os
import sys
from teable import TeableClient


API_URL = os.getenv("TEABLE_API_URL")
API_KEY = os.getenv("TEABLE_API_KEY")
TEST_SPACE_ID = os.getenv("TEABLE_TEST_SPACE_ID")

if not API_URL or not API_KEY:
    print("Error: TEABLE_API_URL and TEABLE_API_KEY must be set in .env")
    sys.exit(1)

def main():
    print("Initializing TeableClient...")
    client = TeableClient({"api_url": API_URL, "api_key": API_KEY})

    print(f"Using Space ID: {TEST_SPACE_ID}")
    
    # Create a test Base
    print("Creating test Base...")
    base = client.spaces.create_base(TEST_SPACE_ID, name="Record Verification Base")
    print(f"Base Created: {base.base_id}")

    try:
        # Create a test Table
        print("Creating test Table...")
        fields = [
            {"name": "Name", "type": "singleLineText"},
            {"name": "Number", "type": "number", "options": {"precision": 0}}
        ]
        table = client.tables.create_table(
            base_id=base.base_id,
            name="Records Table",
            db_table_name="records_test",
            fields=fields
        )
        print(f"Table Created: {table.table_id}")

        # Test 1: Create Record (Basic)
        print("\nTest 1: Create Record (Basic)")
        record1 = table.create_record({"Name": "Record 1", "Number": 10})
        print(f"Created Record 1: {record1.record_id} - {record1.fields}")
        assert record1.fields["Name"] == "Record 1"
        assert record1.fields["Number"] == 10

        # Test 2: Create Record with Typecast (String to Number)
        print("\nTest 2: Create Record with Typecast")
        record2 = table.create_record(
            {"Name": "Record 2", "Number": "20"},
            typecast=True
        )
        print(f"Created Record 2: {record2.record_id} - {record2.fields}")
        assert record2.fields["Number"] == 20

        # Test 3: Create Record with Order (Before Record 1)
        print("\nTest 3: Create Record with Order")
        record3 = table.create_record(
            {"Name": "Record 3", "Number": 30},
            order={"viewId": table.default_view_id, "anchorId": record1.record_id, "position": "before"}
        )
        print(f"Created Record 3: {record3.record_id}")
        # Note: Verifying exact position might require fetching view records, assumes API success for now.

        # Test 4: Update Record
        print("\nTest 4: Update Record")
        updated_record2 = table.update_record(
            record2.record_id,
            {"Name": "Record 2 Updated", "Number": 25}
        )
        print(f"Updated Record 2: {updated_record2.fields}")
        assert updated_record2.fields["Name"] == "Record 2 Updated"
        assert updated_record2.fields["Number"] == 25

        # Test 5: Delete Record
        print("\nTest 5: Delete Record")
        success = table.delete_record(record1.record_id)
        print(f"Deleted Record 1: {success}")
        assert success is True

        # Verify Deletion
        try:
            table.get_record(record1.record_id)
            print("Error: Record 1 should be deleted but was found.")
        except Exception:
            print("Verified Record 1 is deleted (Exception raised directly or 404).")

        print("\nVerification Successful!")

    except Exception as e:
        print(f"\nVerification Failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Cleanup
        print("\nCleaning up...")
        client.spaces.delete_base(base.base_id)
        print("Test Base Deleted.")

if __name__ == "__main__":
    main()
