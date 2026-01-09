
import pytest
from teable import TeableClient

class TestRealTable:
    @pytest.fixture(scope="class")
    def test_base(self, client: TeableClient):
        # Create a space and base for testing
        space = client.spaces.create_space("Table Test Space")
        base = client.spaces.create_base(space.space_id, "Table Test Base")
        yield base
        # Cleanup
        try:
            client.spaces.permanent_delete_space(space.space_id) 
        except Exception:
            try:
                client.spaces.delete_space(space.space_id)
            except:
                pass

    def test_table_lifecycle(self, client: TeableClient, test_base):
        # 1. Create Table
        table_name = "Test Table Lifecycle"
        db_name = "test_table_lifecycle"
        table = client.tables.create_table(
            base_id=test_base.base_id,
            name=table_name,
            db_table_name=db_name,
            description="Testing table lifecycle",
            order=0
        )
        
        assert table.name == table_name
        assert table.table_id.startswith("tbl")
        
        # 2. Get Tables (Verify get_tables fix)
        # This was the main fix: ensuring get_tables accepts base_id and works
        tables = client.tables.get_tables(test_base.base_id)
        assert len(tables) >= 1
        found = False
        for t in tables:
            if t.table_id == table.table_id:
                found = True
                break
        assert found, "Created table not found in get_tables response"

        # 3. Get Table Details
        fetched_table = client.tables.get_table(table.table_id, test_base.base_id)
        assert fetched_table.name == table_name
        assert fetched_table.description == "Testing table lifecycle"
        # Check new fields
        # Note: API responses might differ slightly, but we expect these to be populated if available
        # Order might be 0
        if fetched_table.order is not None:
            assert isinstance(fetched_table.order, int)
        
        # 4. Update Table (Name)
        new_name = "Updated Table Name"
        client.tables.update_table_name(test_base.base_id, table.table_id, new_name)
        
        updated_table = client.tables.get_table(table.table_id, test_base.base_id)
        assert updated_table.name == new_name
        
        # 5. Delete Table
        assert client.tables.delete_table(test_base.base_id, table.table_id) is True
