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
        fake_pub.subscribe('b2_calculated', 'sqrt_calculated')
        fake_pub.listen = lambda : [
            {
                'type': 'subscribe', 'pattern': None,
                'channel': b'b2_calculated', 'data': json.dumps({'4ac': 16, 'a': 1, 'b': 2, 'c': 3})
            },
            {
                'type': 'subscribe', 'pattern': None,
                'channel': b'b2_calculated', 'data': json.dumps({'4ac': 24, 'a': 6, 'b': 5, 'c': 1, 'sqrt': 1})
            },

        ]
        return fake_redis, fake_pub

    # @patch('server.redis.Redis', return_value=fakeredis.FakeConnection())

    def test_calculate_subtract_success(self):

        with patch('redis_connection.make_redis_connection') as make_redis_connection:
            redis_conn, redis_sub = self.make_redis_connection_mock()
            make_redis_connection.return_value = (redis_conn, redis_sub)
            from server import calculate_subtract, handle_message

            num_1 = 10
            num_2 = 3
            expected_result = {'sub': 7}
            result, status_code = calculate_subtract(num_1, num_2)
            self.assertEqual(result, expected_result)
            self.assertEqual(status_code, 200)

    def test_calculate_power_invalid_request(self):
        with patch('redis_connection.make_redis_connection') as make_redis_connection:
            redis_conn, redis_sub = self.make_redis_connection_mock()
            make_redis_connection.return_value = (redis_conn, redis_sub)
            from server import calculate_subtract, handle_message

            num_1 = 'Not a Number'
            num_2 = 2
            expected_result = ("Error: Args should be numbers", 400)
            result, status_code = calculate_subtract(num_1, num_2)
            self.assertEqual(result, expected_result[0])
            self.assertEqual(status_code, 400)


class TestHandleMessage(unittest.TestCase):
    def make_redis_connection_mock(self):
        fake_redis = fakeredis.FakeRedis()
        fake_pub = fake_redis.pubsub()
        # fake_pub = {'subscribe': lambda x: x}
        fake_pub.subscribe('b2_calculated', 'sqrt_calculated')
        fake_pub.listen = lambda : [
            {
                'type': 'subscribe', 'pattern': None,
                'channel': b'b2_calculated', 'data': json.dumps({'4ac': 16, 'a': 1, 'b': 2, 'c': 3})
            },
            {
                'type': 'subscribe', 'pattern': None,
                'channel': b'sqrt_calculated', 'data': json.dumps({'4ac': 24, 'a': 6, 'b': 5, 'c': 1, 'sqrt': 1, 'b_squared': 25})
            },

        ]
        return fake_redis, fake_pub

    @patch('server.calculate_subtract')
    def test_handle_message_valid_message_for_b2calculated(self, mock_calculate_subtract):
        with patch('redis_connection.make_redis_connection') as make_redis_connection, patch('server.redis_conn') as redis_conn_mock, patch('server.redis_conn.publish') as redis_conn_publish_mock :
            redis_conn, redis_sub = self.make_redis_connection_mock()
            make_redis_connection.reset_mock()
            make_redis_connection.return_value = (redis_conn, redis_sub)
            redis_conn_mock.return_value = redis_conn
            redis_conn_publish_mock.return_value = lambda key, data: None
            redis_conn_mock.reset_mock()
            redis_conn_publish_mock.reset_mock()
            from server import calculate_subtract, handle_message

            data = {'4ac': 16, 'a': 1, 'b': 2, 'c': 3, 'b_squared': 4}
            message = {'data': json.dumps(data), 'channel': b'b2_calculated'}
            # redis_conn.publish.return_value = 1
            mock_calculate_subtract.return_value = ({'sub': -12}, 200)
            handle_message(message)
            mock_calculate_subtract.assert_called_once_with(4, 16)

            redis_conn_publish_mock.assert_called_once()

    @patch('server.calculate_subtract')
    def test_handle_message_valid_message_for_sqrt(self, mock_calculate_subtract):
        with patch('redis_connection.make_redis_connection') as make_redis_connection, patch('server.redis_conn') as redis_conn_mock, patch('server.redis_conn.publish') as redis_conn_publish_mock :
            redis_conn, redis_sub = self.make_redis_connection_mock()
            make_redis_connection.reset_mock()
            make_redis_connection.return_value = (redis_conn, redis_sub)
            redis_conn_mock.return_value = redis_conn
            redis_conn_publish_mock.return_value = lambda key, data: None
            redis_conn_mock.reset_mock()
            redis_conn_publish_mock.reset_mock()
            from server import calculate_subtract, handle_message

            data = {'4ac': 24, 'a': 6, 'b': 5, 'c': 1, 'sqrt': 1}
            message = {'data': json.dumps(data), 'channel': b'sqrt_calculated'}
            # redis_conn.publish.return_value = 1
            mock_calculate_subtract.return_value = ({'sub': -6}, 200)
            handle_message(message)
            mock_calculate_subtract.assert_called_once_with(-5, 1)

            redis_conn_publish_mock.assert_called_once()

    @patch('server.calculate_subtract')
    @patch('server.redis_conn')
    def test_handle_message_invalid_message(self, mock_redis_conn, mock_calculate_subtract):
        with patch('redis_connection.make_redis_connection') as make_redis_connection, patch('server.redis_conn') as redis_conn_mock, patch('server.redis_conn.publish') as redis_conn_publish_mock :
            redis_conn, redis_sub = self.make_redis_connection_mock()
            make_redis_connection.reset_mock()
            make_redis_connection.return_value = (redis_conn, redis_sub)
            redis_conn_mock.return_value = redis_conn
            redis_conn_publish_mock.return_value = lambda key, data: None
            redis_conn_mock.reset_mock()
            redis_conn_publish_mock.reset_mock()
            from server import calculate_subtract, handle_message

            data = {'a': 1, 'b': 2, 'c': 3}
            message = {'data': json.dumps(data), 'channel': b'b2_calculated'}
            handle_message(message)
            mock_calculate_subtract.assert_not_called()
            mock_redis_conn.publish.assert_not_called()
