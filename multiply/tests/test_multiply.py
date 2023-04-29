from server import api
import json
import unittest
from unittest.mock import patch


class MultiplyTest(unittest.TestCase):
    def setUp(self):
        self.app = api.test_client()
        self.app.testing = True

    def test_multiply(self):
        with patch('server.redis_conn.publish') as publish_mock:
            coeffs = {'a': 1, 'b': -5, 'c': 6}
            response = api.test_client().post('/multiply', json=coeffs)
            data = json.loads(response.data)
            status_code = response.status_code

            assert status_code == 200
            assert data['4ac'] == 24
            assert data['2a'] == 2
            publish_mock.assert_called_once()

    def test_multiply_wrong_value(self):
        response = api.test_client().post('/multiply', json={"a" : 'test_value'})
        status_code = response.status_code
        with patch('server.redis_conn.publish') as publish_mock:
            publish_mock.reset_mock()

            assert status_code == 400
            publish_mock.assert_not_called()
