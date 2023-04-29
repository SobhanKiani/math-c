import logging
from redis_connection import make_redis_connection
import time
import psutil
from prometheus_client import Counter, Histogram, Gauge, Summary,  start_http_server
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


REQUEST_LATENCY = Histogram('calculate_division_latency_seconds',
                            'Calculate division request latency', ['method'])
REQUEST_COUNT = Counter('calculate_division_request_count',
                        'Calculate division request count', ['method', 'status'])
CPU_USAGE = Gauge('calculate_division_cpu_usage', 'Calculate division CPU usage')
RAM_USAGE = Gauge('calculate_division_ram_usage', 'Calculate division RAM usage')
REQUEST_TIME = Summary('request_processing_seconds', 'Time spent processing request')


def get_connection():
    redis_conn, redis_sub = make_redis_connection()
    return redis_conn, redis_sub


redis_conn, redis_sub = get_connection()


@REQUEST_TIME.time()
def calculate_division(nom, denom):
    start_time = time.time()
    REQUEST_COUNT.labels(method='calculate_division', status='success').inc()

    if not isinstance(nom, int) and not isinstance(denom, int):
        return "Error: Numbers Should Be Int", 400

    if denom == 0:
        return "Error: Can't Devide By 0", 400

    try:
        result = nom / denom

        REQUEST_LATENCY.labels(method='calculate_division').observe(time.time() - start_time)
        REQUEST_COUNT.labels(method='calculate_division', status='success').inc()

        # Update CPU and RAM usage metrics
        CPU_USAGE.set(psutil.cpu_percent())
        RAM_USAGE.set(psutil.virtual_memory().percent)

        return {'division': result}, 200
    except TypeError:
        REQUEST_COUNT.labels(method='calculate_division', status='error').inc()
        return 'Error: Numbers Should Be Int', 400


def handle_message(message):
    data = json.loads(message['data'])
    if message['channel'] == b'nominator_2_calculated':
        if 'nominator_2' in data and 'nominator_1' in data and '2a' in data:
            nom_1 = data['nominator_1']
            nom_2 = data['nominator_2']
            a2 = data['2a']
            first_result, status_code = calculate_division(nom_1, a2)
            second_result, status_code = calculate_division(nom_2, a2)
            # first_result = calculate_division(nom_1, a2)
            # second_result = calculate_division(nom_2, a2)

            print(f"Result 1: {first_result['division']}")
            print(f"Result 2: {second_result['division']}")
        else:
            print("Invalid message recieved")
    else:
        print("Invalid message received")


start_http_server(8080)

for message in redis_sub.listen():
    if not isinstance(message['data'], int):
        handle_message(message=message)
