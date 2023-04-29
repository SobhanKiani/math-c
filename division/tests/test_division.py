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
                'channel': b'under_radical_calculated', 'data': json.dumps({'4ac': 24, 'a': 6, 'b': 5, 'c': 1, '2a': 12, 'nominator_1': -6, 'under_radical': 1, 'nominator_2': -4})
            },
        ]
        return fake_redis, fake_pub

    # @patch('server.redis.Redis', return_value=fakeredis.FakeConnection())

    def test_calculate_division_success(self):

        with patch('redis_connection.make_redis_connection') as make_redis_connection:
            redis_conn, redis_sub = self.make_redis_connection_mock()
            make_redis_connection.return_value = (redis_conn, redis_sub)
            from server import calculate_division, handle_message

            nom = 30
            denom = 6
            expected_result = {'division': nom / denom}
            result, status_code = calculate_division(nom , denom)
            self.assertEqual(result, expected_result)
            self.assertEqual(status_code, 200)

    def test_calculate_division_zero_denom(self):

        with patch('redis_connection.make_redis_connection') as make_redis_connection:
            redis_conn, redis_sub = self.make_redis_connection_mock()
            make_redis_connection.return_value = (redis_conn, redis_sub)
            from server import calculate_division, handle_message

            nom = 30
            denom = 0
            expected_result = "Error: Can't Devide By 0"
            result, status_code = calculate_division(nom, denom)
            self.assertEqual(result, expected_result)
            self.assertEqual(status_code, 400)

    def test_calculate_divison_invalid_request(self):
        with patch('redis_connection.make_redis_connection') as make_redis_connection:
            redis_conn, redis_sub = self.make_redis_connection_mock()
            make_redis_connection.return_value = (redis_conn, redis_sub)
            from server import calculate_division, handle_message

            nom = 'Not a Number'
            denom = 1
            expected_result = ("Error: Numbers Should Be Int", 400)
            result, status_code = calculate_division(nom, denom)
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
                'channel': b'under_radical_calculated', 'data': json.dumps({'4ac': 24, 'a': 6, 'b': 5, 'c': 1, 'division': 1, 'nominator_1': -6, 'under_radical': 1, 'nominator_2': -4})
            },
        ]
        return fake_redis, fake_pub

    @patch('server.calculate_division')
    def test_handle_message_valid_message_for_nominator_1_calculated(self, mock_calculate_division):
        with patch('redis_connection.make_redis_connection') as make_redis_connection, patch('server.redis_conn') as redis_conn_mock, patch('server.redis_conn.publish') as redis_conn_publish_mock :
            redis_conn, redis_sub = self.make_redis_connection_mock()
            make_redis_connection.reset_mock()
            make_redis_connection.return_value = (redis_conn, redis_sub)
            redis_conn_mock.return_value = redis_conn
            redis_conn_publish_mock.return_value = lambda key, data: None
            redis_conn_mock.reset_mock()
            redis_conn_publish_mock.reset_mock()
            from server import calculate_division, handle_message

            data = {'4ac': 24, 'a': 6, 'b': 5, 'c': 1, 'division': 1,
                    'nominator_1': -6, 'under_radical': 1, 'nominator_2': -4, '2a': 12}
            message = {'data': json.dumps(data), 'channel': b'nominator_2_calculated'}
            # redis_conn.publish.return_value = 1
            mock_calculate_division.side_effect = lambda x, y: ({'division': x / y}, 200)
            handle_message(message)
            nom_1 = data['nominator_1']
            nom_2 = data['nominator_2']
            denom = data['2a']

            mock_calculate_division.assert_any_call(nom_1, denom)
            mock_calculate_division.assert_called_with(nom_2, denom)

    @patch('server.calculate_division')
    @patch('server.redis_conn')
    def test_handle_message_invalid_message(self, mock_redis_conn, mock_calculate_division):
        with patch('redis_connection.make_redis_connection') as make_redis_connection, patch('server.redis_conn') as redis_conn_mock, patch('server.redis_conn.publish') as redis_conn_publish_mock :
            redis_conn, redis_sub = self.make_redis_connection_mock()
            make_redis_connection.reset_mock()
            make_redis_connection.return_value = (redis_conn, redis_sub)
            redis_conn_mock.return_value = redis_conn
            redis_conn_publish_mock.return_value = lambda key, data: None
            redis_conn_mock.reset_mock()
            redis_conn_publish_mock.reset_mock()
            from server import calculate_division, handle_message

            data = {'a': 1, 'b': 2, 'c': 3}
            message = {'data': json.dumps(data), 'channel': b'under_radical_calculated'}
            handle_message(message)
            mock_calculate_division.assert_not_called()


