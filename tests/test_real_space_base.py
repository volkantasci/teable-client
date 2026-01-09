
import pytest
from teable import TeableClient

class TestRealSpaceBase:
    @pytest.fixture(scope="class")
    def test_space(self, client: TeableClient):
        # Create a space for testing
        space_name = "Test Space Integration"
        space = client.spaces.create_space(space_name)
        yield space
        # Cleanup
        try:
            client.spaces.delete_space(space.space_id)
        except Exception:
            pass

    def test_update_space(self, client: TeableClient, test_space):
        new_name = "Updated Test Space"
        updated_space = client.spaces.update_space(test_space.space_id, new_name)
        assert updated_space.name == new_name
        assert updated_space.space_id == test_space.space_id

    def test_create_and_delete_base(self, client: TeableClient, test_space):
        base_name = "Test Base"
        base = client.spaces.create_base(test_space.space_id, base_name)
        assert base.name == base_name
        
        # Test update base
        new_base_name = "Updated Base"
        updated_base = client.spaces.update_base(base.base_id, name=new_base_name)
        assert updated_base.name == new_base_name
        
        # Test delete base
        assert client.spaces.delete_base(base.base_id) is True

    def test_get_collaborators(self, client: TeableClient, test_space):
        collabs = client.spaces.list_collaborators(test_space.space_id)
        assert 'collaborators' in collabs
        assert collabs['total'] >= 1
