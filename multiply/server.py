import logging
from flask import Flask, jsonify, request
from prometheus_flask_exporter import PrometheusMetrics
import redis
import json
from redis_connection import make_redis_connection
import time
from prometheus_client import Counter, Histogram, Gauge, start_http_server
import psutil

logging.basicConfig(level=logging.INFO)
logging.info("Setting LOGLEVEL to INFO")

api = Flask(__name__)
metrics = PrometheusMetrics(api)

metrics.info("multiply_microservice_info",
             "The information of multiply microservice", version="1.0.0")

redis_conn = redis.Redis(host='broker', port=6379)


@api.route('/multiply', methods=['POST'])
def calculate_multiply():

    data = request.get_json()
    if not data:
        return 'Error: request must contain a JSON object with a,b,c keys', 400

    a = data['a']
    if not isinstance(a, int):
        return 'Error: a is a number', 400
    try:

        ac4 = data['a'] * data['c'] * 4
        a2 = data['a'] * 2
        redis_conn.publish('multiplies_calculated', json.dumps({'4ac': ac4, '2a': a2 , **data}))
        print("multiplies_calculated event published")
        return {'4ac': ac4, '2a': a2}, 200
    except TypeError:
        return 'Error: request must contain a JSON array of numbers.', 400
