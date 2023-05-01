import logging
import json
# import redis
import time
import psutil
from prometheus_client import Counter, Histogram, Gauge, start_http_server
from redis_connection import make_redis_connection
import sys

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)
logger.info('This is an info message')


REQUEST_LATENCY = Histogram('calculate_power_latency_seconds',
                            'Calculate Power request latency', ['method'])
REQUEST_COUNT = Counter('calculate_power_request_count',
                        'Calculate Power request count', ['method', 'status'])
CPU_USAGE = Gauge('calculate_power_cpu_usage', 'Calculate Power CPU usage')
RAM_USAGE = Gauge('calculate_power_ram_usage', 'Calculate Power RAM usage')


def get_connection():
    redis_conn, redis_sub = make_redis_connection()
    return redis_conn, redis_sub


redis_conn, redis_sub = get_connection()


def calculate_power(base, exponent, *args, **kwargs):
    start_time = time.time()
    REQUEST_COUNT.labels(method='calculate_power', status='success').inc()

    if base == 0:
        REQUEST_COUNT.labels(method='calculate_power', status='error').inc()
        return "Error: base cannot be 0", 400

    try:
        total = base ** exponent

        # Send b^2_calculated event

        REQUEST_LATENCY.labels(method='calculate_power').observe(time.time() - start_time)
        REQUEST_COUNT.labels(method='calculate_power', status='success').inc()

        # Update CPU and RAM usage metrics
        CPU_USAGE.set(psutil.cpu_percent())
        RAM_USAGE.set(psutil.virtual_memory().percent)

        return {'power': total}, 200
    except TypeError:
        REQUEST_COUNT.labels(method='calculate_power', status='error').inc()
        return 'Error: request must contain a JSON array of numbers.', 400


def handle_message(message):
    data = json.loads(message['data'])
    if '4ac' in data and 'a' in data and 'b' in data and 'c' in data:
        base = data['b']
        exponent = 2
        result, status_code = calculate_power(
            base, exponent, kwargs=data)
        redis_conn.publish('b2_calculated', json.dumps(
            {'b_squared': result['power'], **data}))

        # print(f"b^2_calculated event published with value: {base ** 2}")
        logger.info(f"b^2_calculated event published with value: {base ** 2}")
    else:
        print("Invalid message received")


start_http_server(8080)

for message in redis_sub.listen():
    if not isinstance(message['data'], int):
        handle_message(message=message)
# redis_sub.set_callback(handle_message)
# redis_sub.run_in_thread(sleep_time=0.001)
  