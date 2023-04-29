import logging
from flask import Flask, jsonify, request
from prometheus_flask_exporter import PrometheusMetrics
import json
import services

logging.basicConfig(level=logging.INFO)
logging.info("Setting LOGLEVEL to INFO")

api = Flask(__name__)
metrics = PrometheusMetrics(api)

metrics.info("gateway_microservice_info",
             "The information of gateway microservice", version="1.0.0")


# def handle_api_error(response):
#     try:
#         content = json.loads(response.content)
#         if isinstance(content, dict) and 'error' in content:
#             return content['error']
#         else:
#             return "API Error: " + response.content.decode('utf-8')
#     except Exception:
#         return "API Error: " + response.content.decode('utf-8')


@api.route('/equation', methods=['POST'])
def calculate_equation():

    data = request.get_json()
    a = data['a']
    b = data['b']
    c = data['c']

    if not isinstance(a, int) or not isinstance(b, int) or not isinstance(c, int):
        return "Error: All of the coeffs should be numbers", 400

    try:
        ac4 = services.post_multiply({'a': a, 'b': b, 'c': c})
        return {"result": 'The Equation Is Being Calculated', '4ac': ac4}, 200
    except Exception as e:
        return e
