import logging
from flask import Flask, jsonify, request
from prometheus_flask_exporter import PrometheusMetrics
from redis_connection import make_redis_connection
import time
import psutil
from prometheus_client import Counter, Histogram, Gauge, start_http_server
import json
import sys


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)
logger.info('This is an info message')


REQUEST_LATENCY = Histogram('calculate_subtract_latency_seconds',
                            'Calculate subtract request latency', ['method'])
REQUEST_COUNT = Counter('calculate_subtract_request_count',
                        'Calculate subtract request count', ['method', 'status'])
CPU_USAGE = Gauge('calculate_subtract_cpu_usage', 'Calculate subtract CPU usage')
RAM_USAGE = Gauge('calculate_subtract_ram_usage', 'Calculate subtract RAM usage')


def get_connection():
    redis_conn, redis_sub = make_redis_connection()
    return redis_conn, redis_sub


redis_conn, redis_sub = get_connection()


def calculate_subtract(num_1, num_2):
    start_time = time.time()
    REQUEST_COUNT.labels(method='calculate_subtract', status='success').inc()

    if not isinstance(num_1, int) or not isinstance(num_2, int):
        return "Error: Args should be numbers", 400

    try:
        result = num_1 - num_2

        REQUEST_LATENCY.labels(method='calculate_subtract').observe(time.time() - start_time)
        REQUEST_COUNT.labels(method='calculate_subtract', status='success').inc()

        # Update CPU and RAM usage metrics
        CPU_USAGE.set(psutil.cpu_percent())
        RAM_USAGE.set(psutil.virtual_memory().percent)

        return {'sub': result}, 200
    except TypeError:
        REQUEST_COUNT.labels(method='calculate_subtract', status='error').inc()
        return 'Error: request must contain a JSON array of numbers.', 400


def handle_message(message):
    data = json.loads(message['data'])
    if message['channel'] == b'b2_calculated':
        if '4ac' in data and 'b_squared' in data:
            ac4 = data['4ac']
            b_squared = data['b_squared']

            result, status_code = calculate_subtract(b_squared, ac4)

            redis_conn.publish('under_radical_calculated', json.dumps(
                {**data, 'under_radical': result['sub']}
            ))

            logger.info(f"Under Radical event published with value: {result['sub']}")
    elif message['channel'] == b'sqrt_calculated':
        if 'b' in data and 'sqrt' in data:
            b = data['b']
            sqrt = data['sqrt']
            result, status_code = calculate_subtract(-b, sqrt)
            redis_conn.publish('nominator_1_calculated', json.dumps(
                {**data, 'nominator_1': result['sub']}
            ))

            logger.info(f"Nominator_1 event published with value: {result['sub']}")

    else:
        print("Invalid message received")


start_http_server(8080)

for message in redis_sub.listen():
    if not isinstance(message['data'], int):
        handle_message(message=message)
 