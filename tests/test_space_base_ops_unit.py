import unittest
from unittest.mock import MagicMock
from teable.core.spaces import SpaceManager
from teable.core.http import TeableHttpClient
from teable.core.cache import ResourceCache

class TestSpaceManagerBaseOpsUnit(unittest.TestCase):
    def setUp(self):
        self.http_client = MagicMock(spec=TeableHttpClient)
        self.space_cache = MagicMock(spec=ResourceCache)
        self.base_cache = MagicMock(spec=ResourceCache)
        self.space_manager = SpaceManager(self.http_client, self.space_cache, self.base_cache)

    def test_list_base_collaborators(self):
        expected = {"collaborators": [], "total": 0}
        self.http_client.request.return_value = expected
        res = self.space_manager.list_base_collaborators("base1")
        self.http_client.request.assert_called_with(
            'GET', 
            '/base/base1/collaborators', 
            params={}
        )
        self.assertEqual(res, expected)

    def test_update_base_collaborator(self):
        self.http_client.request.return_value = {}
        self.space_manager.update_base_collaborator("base1", "user1", "user", "editor")
        self.http_client.request.assert_called_with(
            'PATCH',
            '/base/base1/collaborators',
            json={'principalId': 'user1', 'principalType': 'user', 'role': 'editor'}
        )

    def test_delete_base_collaborator(self):
        self.http_client.request.return_value = {}
        self.space_manager.delete_base_collaborator("base1", "user1", "user")
        self.http_client.request.assert_called_with(
            'DELETE',
            '/base/base1/collaborators',
            params={'principalId': 'user1', 'principalType': 'user'}
        )

if __name__ == '__main__':
    unittest.main()
