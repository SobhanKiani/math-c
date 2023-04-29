import json
import unittest
from unittest.mock import patch
from server import api
import math


class EquationEndpointTestCase(unittest.TestCase):

    def setUp(self):
        self.app = api.test_client()
        self.app.testing = True

    def test_calculate_equation_valid_input(self):

        with patch('services.post_multiply') as mock_multiply:

            data = {'a': 1, 'b': -5, 'c': 6}

            mock_multiply.side_effect = lambda x: {
                'result': "The Equation Is Being Calculated", 'status_code': 200}

            response = self.app.post('/equation', json=data)
        
            expected_result = {'result': "The Equation Is Being Calculated", 'status_code': 200}
            self.assertEqual(response.status_code, expected_result['status_code'])    
            self.assertEqual(response.json['result'], expected_result['result'])

            # mock_multiply.assert_any_call([2, data['a']])
            # mock_power.assert_called_once_with({'base': data['b'], 'exponent': 2})
            # # mock_sqrt.assert_called_once_with({'number': 1})
            # mock_sum.assert_called_once_with({'numbers': [-data['b'], mock_sqrt.return_value]})
            # mock_sub.assert_any_call(
            #     {'numbers': [mock_power.return_value, mock_multiply.return_value * data['c']]})

    def test_calculate_equation_invalid_input(self):
        data = {'a': 3, 'b': 'not_a_number', 'c': -1}
        response = self.app.post('/equation', data=json.dumps(data),
                                 content_type='application/json')
        print(response.data)

        expected_result = {
            "result": b'Error: All of the coeffs should be numbers', 'status_code': 400}
        self.assertEqual(response.status_code, expected_result['status_code'])
        self.assertEqual(response.data, expected_result['result'])

    def test_calculate_equation_no_real_roots(self):
        with patch('services.post_multiply') as mock_multiply:

            mock_multiply.return_value = 12

            data = {'a': 1, 'b': 2, 'c': 3}
            response = self.app.post('/equation', data=json.dumps(data),
                                     content_type='application/json')

            expected_result = {'result': "The Equation Is Being Calculated", 'status_code': 200}
            self.assertEqual(response.status_code, expected_result['status_code'])
            self.assertEqual(response.json['result'], expected_result['result'])
