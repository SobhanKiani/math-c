import json
import unittest
from unittest.mock import patch
import fakeredis
import json


class TestCalculatePower(unittest.TestCase):

    def make_redis_connection_mock(self):
        fake_redis = fakeredis.FakeRedis()
        fake_pub = fake_redis.pubsub()
        fake_pub.subscribe('nominator_1_calculated')
        fake_pub.listen = lambda : [
            {
                'type': 'subscribe', 'pattern': None,
                'channel': b'nominator_1_calculated', 'data': json.dumps({'4ac': 24, 'a': 6, 'b': 5, 'c': 1, 'sqrt': 1, 'nominator_1': -6})
            },
        ]
        return fake_redis, fake_pub

    # @patch('server.redis.Redis', return_value=fakeredis.FakeConnection())

    def test_calculate_sum_success(self):

        with patch('redis_connection.make_redis_connection') as make_redis_connection:
            redis_conn, redis_sub = self.make_redis_connection_mock()
            make_redis_connection.return_value = (redis_conn, redis_sub)
            from server import calculate_sum, handle_message

            num_1 = 10
            num_2 = 3
            expected_result = {'sum': 13}
            result, status_code = calculate_sum(num_1, num_2)
            self.assertEqual(result, expected_result)
            self.assertEqual(status_code, 200)

    def test_calculate_power_invalid_request(self):
        with patch('redis_connection.make_redis_connection') as make_redis_connection:
            redis_conn, redis_sub = self.make_redis_connection_mock()
            make_redis_connection.return_value = (redis_conn, redis_sub)
            from server import calculate_sum, handle_message

            num_1 = 'Not a Number'
            num_2 = 2
            expected_result = ("Error: Args should be numbers", 400)
            result, status_code = calculate_sum(num_1, num_2)
            self.assertEqual(result, expected_result[0])
            self.assertEqual(status_code, 400)


class TestHandleMessage(unittest.TestCase):
    def make_redis_connection_mock(self):
        fake_redis = fakeredis.FakeRedis()
        fake_pub = fake_redis.pubsub()
        # fake_pub = {'subscribe': lambda x: x}
        fake_pub.subscribe('nominator_1_calculated')
        fake_pub.listen = lambda : [
            {
                'type': 'subscribe', 'pattern': None,
                'channel': b'nominator_1_calculated', 'data': json.dumps({'4ac': 24, 'a': 6, 'b': 5, 'c': 1, 'sqrt': 1, 'b_squared': 25, 'nominator_1': -6})
            },

        ]
        return fake_redis, fake_pub

    @patch('server.calculate_sum')
    def test_handle_message_valid_message_for_nominator_1_calculated(self, mock_calculate_sum):
        with patch('redis_connection.make_redis_connection') as make_redis_connection, patch('server.redis_conn') as redis_conn_mock, patch('server.redis_conn.publish') as redis_conn_publish_mock :
            redis_conn, redis_sub = self.make_redis_connection_mock()
            make_redis_connection.reset_mock()
            make_redis_connection.return_value = (redis_conn, redis_sub)
            redis_conn_mock.return_value = redis_conn
            redis_conn_publish_mock.return_value = lambda key, data: None
            redis_conn_mock.reset_mock()
            redis_conn_publish_mock.reset_mock()
            from server import calculate_sum, handle_message

            data = {'4ac': 24, 'a': 6, 'b': 5, 'c': 1,
                    'sqrt': 1, 'b_squared': 25, 'nominator_1': -6}
            message = {'data': json.dumps(data), 'channel': b'nominator_1_calculated'}
            # redis_conn.publish.return_value = 1
            mock_calculate_sum.return_value = ({'sum': -4}, 200)
            handle_message(message)
            mock_calculate_sum.assert_called_once_with(-5, 1)

            redis_conn_publish_mock.assert_called_once()

    @patch('server.calculate_sum')
    @patch('server.redis_conn')
    def test_handle_message_invalid_message(self, mock_redis_conn, mock_calculate_sum):
        with patch('redis_connection.make_redis_connection') as make_redis_connection, patch('server.redis_conn') as redis_conn_mock, patch('server.redis_conn.publish') as redis_conn_publish_mock :
            redis_conn, redis_sub = self.make_redis_connection_mock()
            make_redis_connection.reset_mock()
            make_redis_connection.return_value = (redis_conn, redis_sub)
            redis_conn_mock.return_value = redis_conn
            redis_conn_publish_mock.return_value = lambda key, data: None
            redis_conn_mock.reset_mock()
            redis_conn_publish_mock.reset_mock()
            from server import calculate_sum, handle_message

            data = {'a': 1, 'b': 2, 'c': 3}
            message = {'data': json.dumps(data), 'channel': b'nominator_1_calculated'}
            handle_message(message)
            mock_calculate_sum.assert_not_called()
            mock_redis_conn.publish.assert_not_called()
