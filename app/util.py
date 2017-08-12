import random
import string

import redis

from app import REDIS_HOST, REDIS_PORT, REDIS_DB


def get_random_string(n):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=n))


def get_redis_connect():
    pool = redis.ConnectionPool(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)
    r = redis.Redis(connection_pool=pool)
    return r
