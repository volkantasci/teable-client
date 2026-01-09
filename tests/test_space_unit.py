import unittest
from unittest.mock import MagicMock
from teable.core.spaces import SpaceManager
from teable.core.http import TeableHttpClient
from teable.core.cache import ResourceCache

class TestSpaceManagerUnit(unittest.TestCase):
    def setUp(self):
        self.http_client = MagicMock(spec=TeableHttpClient)
        self.space_cache = MagicMock(spec=ResourceCache)
        self.base_cache = MagicMock(spec=ResourceCache)
        self.space_manager = SpaceManager(self.http_client, self.space_cache, self.base_cache)

    def test_get_space_authentication(self):
        expected = {"auth": True}
        self.http_client.request.return_value = expected
        res = self.space_manager.get_space_authentication("spc123")
        self.http_client.request.assert_called_with('GET', '/space/spc123/authentication')
        self.assertEqual(res, expected)

    def test_update_space_authentication(self):
        settings = {"auth": False}
        self.http_client.request.return_value = settings
        res = self.space_manager.update_space_authentication("spc123", settings)
        self.http_client.request.assert_called_with(
            'PATCH',
            '/space/spc123/authentication',
            json=settings
        )
        self.assertEqual(res, settings)

    def test_delete_space_authentication(self):
        self.http_client.request.return_value = None
        self.space_manager.delete_space_authentication("spc123")
        self.http_client.request.assert_called_with('DELETE', '/space/spc123/authentication')

if __name__ == '__main__':
    unittest.main()
