import os
import random
import string
import time

import redis


def get_random_string(n):
    """ Create random string with len `n`
    """
    return ''.join(random.choices(string.ascii_letters + string.digits, k=n))


def get_redis_connect():
    """ Create connection instance
    """
    from service.C import REDIS_HOST, REDIS_PORT, REDIS_DB
    pool = redis.ConnectionPool(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)
    r = redis.Redis(connection_pool=pool)
    return r


def get_succes_chance():
    """ Return chance of 5% for mailformed message
    """
    return random.randint(1,20) != 1


def is_errors_request(get_errors=None):
    if os.environ.get('GET_ERRORS', get_errors):
        return True

def is_clean_request(clean=None):
    if os.environ.get('CLEAN_DB', clean):
        return True


def get_time_in_ms():
    return int(round(time.time() * 1000))
