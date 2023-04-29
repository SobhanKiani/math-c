import requests
from utils import SUM_URL, SUBTRACT_URL, MULTIPLY_URL, DIVISION_URL, POWER_URL, SQRT_URL, REPRESENTATION_SAVE_URL
import json


def post_multiply(data):
    result = requests.post(MULTIPLY_URL, json={'a': data['a'], 'b': data['b'], 'c': data['c']})
    if result.ok:
        return json.loads(result.content)['4ac']
    else:
        return result.content


# def post_power(args):
#     result = requests.post(POWER_URL, json=args)
#     if result.ok:
#         return json.loads(result.content)['power']
#     else:
        return result.content


# def post_sub(args):
#     result = requests.post(SUBTRACT_URL, json=args)
#     if result.ok:
#         return json.loads(result.content)['subtract']
#     else:
#         return result.content


# def post_division(args):
#     result = requests.post(DIVISION_URL, json=args)
#     if result.ok:
#         return json.loads(result.content)['division']
#     else:
#         return result.content


# def post_sum(args):
#     result = requests.post(SUM_URL, json=args)
#     if result.ok:
#         return json.loads(result.content)['sum']
#     else:
#         return result.content


# def post_sqrt(args):
#     result = requests.post(SQRT_URL, json=args)
#     if result.ok:
#         return json.loads(result.content)['sqrt']
#     else:
#         return result.content
