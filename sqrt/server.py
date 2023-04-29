import logging
from flask import Flask, jsonify, request
from prometheus_flask_exporter import PrometheusMetrics
from redis_connection import make_redis_connection
import time
import psutil
from prometheus_client import Counter, Histogram, Gauge, start_http_server
import json
import math
import sys


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)
logger.info('This is an info message')


REQUEST_LATENCY = Histogram('calculate_sqrt_latency_seconds',
                            'Calculate sqrt request latency', ['method'])
REQUEST_COUNT = Counter('calculate_sqrt_request_count',
                        'Calculate sqrt request count', ['method', 'status'])
CPU_USAGE = Gauge('calculate_sqrt_cpu_usage', 'Calculate sqrt CPU usage')
RAM_USAGE = Gauge('calculate_sqrt_ram_usage', 'Calculate sqrt RAM usage')


def get_connection():
    redis_conn, redis_sub = make_redis_connection()
    return redis_conn, redis_sub


redis_conn, redis_sub = get_connection()


def calculate_sqrt(number):
    start_time = time.time()
    REQUEST_COUNT.labels(method='calculate_sqrt', status='success').inc()

    if not isinstance(number, int):
        return "Error: Number Should Be Int", 400

    try:
        if number >= 0:
            result = math.sqrt(number)
        else:
            result = "Negative Number"

        REQUEST_LATENCY.labels(method='calculate_sqrt').observe(time.time() - start_time)
        REQUEST_COUNT.labels(method='calculate_sqrt', status='success').inc()

        # Update CPU and RAM usage metrics
        CPU_USAGE.set(psutil.cpu_percent())
        RAM_USAGE.set(psutil.virtual_memory().percent)

        return {'sqrt': result}, 200
    except TypeError:
        REQUEST_COUNT.labels(method='calculate_sqrt', status='error').inc()
        return 'Error: request must contain a JSON array of numbers.', 400


def handle_message(message):
    data = json.loads(message['data'])

    if message['channel'] == b'under_radical_calculated':
        if 'under_radical' in data:
            under_radical = data['under_radical']
            result, status_code = calculate_sqrt(under_radical)
            if result['sqrt'] != 'Negative Number':
                redis_conn.publish('sqrt_calculated', json.dumps(
                    {**data, 'sqrt': int(result['sqrt'])}
                ))
                logger.info(f"sqrt_calculated event published with value: {int(result['sqrt'])}")
        else:
            logger.info('No Real Roots')
    else:
        print("Invalid message received")


start_http_server(8080)

for message in redis_sub.listen():
    if not isinstance(message['data'], int):
        handle_message(message=message)

 