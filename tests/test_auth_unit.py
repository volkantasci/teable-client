import unittest
from unittest.mock import MagicMock
from teable.core.auth import AuthManager
from teable.core.http import TeableHttpClient

class TestAuthManagerUnit(unittest.TestCase):
    def setUp(self):
        self.http_client = MagicMock(spec=TeableHttpClient)
        self.auth = AuthManager(self.http_client)

    def test_update_user_language(self):
        self.http_client.request.return_value = {}
        self.auth.update_user_language('en')
        self.http_client.request.assert_called_with(
            'PATCH',
            '/user/lang',
            json={'lang': 'en'}
        )

    def test_get_last_visit(self):
        expected_response = {"baseId": "123"}
        self.http_client.request.return_value = expected_response
        res = self.auth.get_last_visit()
        self.http_client.request.assert_called_with('GET', '/user/last-visit')
        self.assertEqual(res, expected_response)

    def test_update_last_visit(self):
        self.http_client.request.return_value = {}
        data = {'baseId': '123'}
        self.auth.update_last_visit(data)
        self.http_client.request.assert_called_with(
            'POST',
            '/user/last-visit',
            json=data
        )

    def test_get_last_visit_base_node(self):
        expected = {"node": "data"}
        self.http_client.request.return_value = expected
        res = self.auth.get_last_visit_base_node()
        self.http_client.request.assert_called_with('GET', '/user/last-visit/base-node')
        self.assertEqual(res, expected)

    def test_get_last_visit_list_base(self):
        expected = {"list": []}
        self.http_client.request.return_value = expected
        res = self.auth.get_last_visit_list_base()
        self.http_client.request.assert_called_with('GET', '/user/last-visit/list-base')
        self.assertEqual(res, expected)

    def test_get_last_visit_map(self):
        expected = {"map": {}}
        self.http_client.request.return_value = expected
        res = self.auth.get_last_visit_map()
        self.http_client.request.assert_called_with('GET', '/user/last-visit/map')
        self.assertEqual(res, expected)

if __name__ == '__main__':
    unittest.main()
