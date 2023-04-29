import redis


def make_redis_connection():
    redis_conn = redis.Redis(host='broker', port=6379, db=0)
    redis_sub = redis_conn.pubsub()
    redis_sub.subscribe('b2_calculated', 'sqrt_calculated')
    return redis_conn, redis_sub
