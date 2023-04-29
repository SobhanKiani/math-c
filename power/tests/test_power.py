import json
import unittest
from unittest.mock import patch
import fakeredis
import json


class TestCalculatePower(unittest.TestCase):

    def make_redis_connection_mock(self):
        fake_redis = fakeredis.FakeRedis()
        fake_pub = fake_redis.pubsub()
        # fake_pub = {'subscribe': lambda x: x}
        fake_pub.subscribe('multiplies_calculated')
        fake_pub.listen = lambda : [{'type': 'subscribe', 'pattern': None,
                                    'channel': b'multiplies_calculated', 'data': json.dumps({'4ac': 16, 'a': 1, 'b': 2, 'c': 3})}]
        return fake_redis, fake_pub

    # @patch('server.redis.Redis', return_value=fakeredis.FakeConnection())

    def test_calculate_power_success(self):

        with patch('redis_connection.make_redis_connection') as make_redis_connection:
            redis_conn, redis_sub = self.make_redis_connection_mock()
            make_redis_connection.return_value = (redis_conn, redis_sub)
            from server import calculate_power, handle_message

            base = 5
            exponent = 2
            expected_result = {'power': 25}
            result, status_code = calculate_power(base, exponent)
            self.assertEqual(result, expected_result)
            self.assertEqual(status_code, 200)

    def test_calculate_power_base_zero(self):
        with patch('redis_connection.make_redis_connection') as make_redis_connection:
            redis_conn, redis_sub = self.make_redis_connection_mock()
            make_redis_connection.return_value = (redis_conn, redis_sub)
            from server import calculate_power, handle_message

            base = 0
            exponent = 2
            expected_result = ("Error: base cannot be 0", 400)
            result, status_code = calculate_power(base, exponent)
            self.assertEqual(result, expected_result[0])
            self.assertEqual(status_code, 400)

    def test_calculate_power_invalid_request(self):
        with patch('redis_connection.make_redis_connection') as make_redis_connection:
            redis_conn, redis_sub = self.make_redis_connection_mock()
            make_redis_connection.return_value = (redis_conn, redis_sub)
            from server import calculate_power, handle_message

            base = 'not a number'
            exponent = 2
            expected_result = ("Error: request must contain a JSON array of numbers.", 400)
            result, status_code = calculate_power(base, exponent)
            self.assertEqual(result, expected_result[0])
            self.assertEqual(status_code, 400)


class TestHandleMessage(unittest.TestCase):
    def make_redis_connection_mock(self):
        fake_redis = fakeredis.FakeRedis()
        fake_pub = fake_redis.pubsub()
        # fake_pub = {'subscribe': lambda x: x}
        fake_pub.subscribe('multiplies_calculated')
        fake_pub.listen = lambda : [{'type': 'subscribe', 'pattern': None,
                                    'channel': b'multiplies_calculated', 'data': json.dumps({'4ac': 16, 'a': 1, 'b': 2, 'c': 3})}]
        return fake_redis, fake_pub

    @patch('server.calculate_power')
    def test_handle_message_valid_message(self, mock_calculate_power):
        with patch('redis_connection.make_redis_connection') as make_redis_connection, patch('server.redis_conn') as redis_conn_mock, patch('server.redis_conn.publish') as redis_conn_publish_mock :
            redis_conn, redis_sub = self.make_redis_connection_mock()
            make_redis_connection.reset_mock()
            make_redis_connection.return_value = (redis_conn, redis_sub)
            redis_conn_mock.return_value = redis_conn
            redis_conn_publish_mock.return_value = lambda key, data: None
            redis_conn_mock.reset_mock()
            redis_conn_publish_mock.reset_mock()
            from server import calculate_power, handle_message

            data = {'4ac': 12, 'a': 1, 'b': 2, 'c': 3}
            message = {'data': json.dumps(data)}
            # redis_conn.publish.return_value = 1
            mock_calculate_power.return_value = ({'power': 4}, 200)
            handle_message(message)
            mock_calculate_power.assert_called_once_with(2, 2, kwargs=data)

            redis_conn_publish_mock.assert_called_once()

    @patch('server.calculate_power')
    @patch('server.redis_conn')
    def test_handle_message_invalid_message(self, mock_redis_conn, mock_calculate_power):
        with patch('redis_connection.make_redis_connection') as make_redis_connection, patch('server.redis_conn') as redis_conn_mock, patch('server.redis_conn.publish') as redis_conn_publish_mock :
            redis_conn, redis_sub = self.make_redis_connection_mock()
            make_redis_connection.reset_mock()
            make_redis_connection.return_value = (redis_conn, redis_sub)
            redis_conn_mock.return_value = redis_conn
            redis_conn_publish_mock.return_value = lambda key, data: None
            redis_conn_mock.reset_mock()
            redis_conn_publish_mock.reset_mock()
            from server import calculate_power, handle_message
            
            data = {'a': 1, 'b': 2, 'c': 3}
            message = {'data': json.dumps(data)}
            handle_message(message)
            mock_calculate_power.assert_not_called()
            mock_redis_conn.publish.assert_not_called()
