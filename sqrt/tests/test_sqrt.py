import json
import unittest
from unittest.mock import patch
import fakeredis
import json


class TestCalculatePower(unittest.TestCase):

    def make_redis_connection_mock(self):
        fake_redis = fakeredis.FakeRedis()
        fake_pub = fake_redis.pubsub()
        fake_pub.subscribe('under_radical_calculated')
        fake_pub.listen = lambda : [
            {
                'type': 'subscribe', 'pattern': None,
                'channel': b'under_radical_calculated', 'data': json.dumps({'4ac': 24, 'a': 6, 'b': 5, 'c': 1, 'sqrt': 1, 'nominator_1': -6, 'under_radical': 1})
            },
        ]
        return fake_redis, fake_pub

    # @patch('server.redis.Redis', return_value=fakeredis.FakeConnection())

    def test_calculate_sqrt_success(self):

        with patch('redis_connection.make_redis_connection') as make_redis_connection:
            redis_conn, redis_sub = self.make_redis_connection_mock()
            make_redis_connection.return_value = (redis_conn, redis_sub)
            from server import calculate_sqrt, handle_message

            num = 25
            expected_result = {'sqrt': 5}
            result, status_code = calculate_sqrt(num)
            self.assertEqual(result, expected_result)
            self.assertEqual(status_code, 200)

    def test_calculate_sqrt_negative_number(self):

        with patch('redis_connection.make_redis_connection') as make_redis_connection:
            redis_conn, redis_sub = self.make_redis_connection_mock()
            make_redis_connection.return_value = (redis_conn, redis_sub)
            from server import calculate_sqrt, handle_message

            num = -25
            expected_result = {'sqrt': 'Negative Number'}
            result, status_code = calculate_sqrt(num)
            self.assertEqual(result, expected_result)
            self.assertEqual(status_code, 200)

    def test_calculate_power_invalid_request(self):
        with patch('redis_connection.make_redis_connection') as make_redis_connection:
            redis_conn, redis_sub = self.make_redis_connection_mock()
            make_redis_connection.return_value = (redis_conn, redis_sub)
            from server import calculate_sqrt, handle_message

            num = 'Not a Number'

            expected_result = ("Error: Number Should Be Int", 400)
            result, status_code = calculate_sqrt(num)
            self.assertEqual(result, expected_result[0])
            self.assertEqual(status_code, 400)


class TestHandleMessage(unittest.TestCase):
    def make_redis_connection_mock(self):
        fake_redis = fakeredis.FakeRedis()
        fake_pub = fake_redis.pubsub()
        fake_pub.subscribe('under_radical_calculated')
        fake_pub.listen = lambda : [
            {
                'type': 'subscribe', 'pattern': None,
                'channel': b'under_radical_calculated', 'data': json.dumps({'4ac': 24, 'a': 6, 'b': 5, 'c': 1, 'sqrt': 1, 'nominator_1': -6, 'under_radical': 1})
            },
        ]
        return fake_redis, fake_pub

    @patch('server.calculate_sqrt')
    def test_handle_message_valid_message_for_nominator_1_calculated(self, mock_calculate_sqrt):
        with patch('redis_connection.make_redis_connection') as make_redis_connection, patch('server.redis_conn') as redis_conn_mock, patch('server.redis_conn.publish') as redis_conn_publish_mock :
            redis_conn, redis_sub = self.make_redis_connection_mock()
            make_redis_connection.reset_mock()
            make_redis_connection.return_value = (redis_conn, redis_sub)
            redis_conn_mock.return_value = redis_conn
            redis_conn_publish_mock.return_value = lambda key, data: None
            redis_conn_mock.reset_mock()
            redis_conn_publish_mock.reset_mock()
            from server import calculate_sqrt, handle_message

            data = {'4ac': 24, 'a': 6, 'b': 5, 'c': 1,
                    'sqrt': 1, 'b_squared': 25, 'nominator_1': -6, 'under_radical': 1}
            message = {'data': json.dumps(data), 'channel': b'under_radical_calculated'}
            # redis_conn.publish.return_value = 1
            mock_calculate_sqrt.return_value = ({'sqrt': 1}, 200)
            handle_message(message)
            mock_calculate_sqrt.assert_called_once_with(1)

            redis_conn_publish_mock.assert_called_once()

    @patch('server.calculate_sqrt')
    def test_handle_message_valid_message_for_nominator_1_calculated(self, mock_calculate_sqrt):
        with patch('redis_connection.make_redis_connection') as make_redis_connection, patch('server.redis_conn') as redis_conn_mock, patch('server.redis_conn.publish') as redis_conn_publish_mock :
            redis_conn, redis_sub = self.make_redis_connection_mock()
            make_redis_connection.reset_mock()
            make_redis_connection.return_value = (redis_conn, redis_sub)
            redis_conn_mock.return_value = redis_conn
            redis_conn_publish_mock.return_value = lambda key, data: None
            redis_conn_mock.reset_mock()
            redis_conn_publish_mock.reset_mock()
            from server import calculate_sqrt, handle_message

            data = {'4ac': 32, 'a': 8, 'b': 5, 'c': 1,
                    'sqrt': 1, 'b_squared': 25, 'under_radical': -7}
            message = {'data': json.dumps(data), 'channel': b'under_radical_calculated'}
            # redis_conn.publish.return_value = 1
            mock_calculate_sqrt.return_value = ({'sqrt': 'Negative Number'}, 200)
            handle_message(message)
            mock_calculate_sqrt.assert_called_once_with(-7)

            redis_conn_publish_mock.assert_not_called()

    @patch('server.calculate_sqrt')
    @patch('server.redis_conn')
    def test_handle_message_invalid_message(self, mock_redis_conn, mock_calculate_sqrt):
        with patch('redis_connection.make_redis_connection') as make_redis_connection, patch('server.redis_conn') as redis_conn_mock, patch('server.redis_conn.publish') as redis_conn_publish_mock :
            redis_conn, redis_sub = self.make_redis_connection_mock()
            make_redis_connection.reset_mock()
            make_redis_connection.return_value = (redis_conn, redis_sub)
            redis_conn_mock.return_value = redis_conn
            redis_conn_publish_mock.return_value = lambda key, data: None
            redis_conn_mock.reset_mock()
            redis_conn_publish_mock.reset_mock()
            from server import calculate_sqrt, handle_message

            data = {'a': 1, 'b': 2, 'c': 3}
            message = {'data': json.dumps(data), 'channel': b'under_radical_calculated'}
            handle_message(message)
            mock_calculate_sqrt.assert_not_called()
            mock_redis_conn.publish.assert_not_called()
