import random
import string
import os

import redis

from app import REDIS_HOST, REDIS_PORT, REDIS_DB


def get_random_string(n):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=n))


def get_redis_connect():
    pool = redis.ConnectionPool(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)
    r = redis.Redis(connection_pool=pool)
    return r

def get_succes_chance():
    return random.randint(1,20) != 1

def is_errors_request(get_errors=None):
    if os.environ.get('GET_ERRORS', get_errors):
        return True