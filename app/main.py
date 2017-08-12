import logging
from time import sleep

from app import APP_NAME
from app.util import get_random_string, get_redis_connect


APP_ID = get_random_string(5)
DEALER_KEY = 'current_dealer'
DEALER_KEY_TTL = 500   # in ms


logger = logging.getLogger('{app}_{id}'.format(app=APP_NAME, id=APP_ID))
logging.basicConfig(level=logging.INFO)


def get_connect():
    pool = redis.ConnectionPool(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)
    r = redis.Redis(connection_pool=pool)
    return r


def read(connection):
    pass


def write():
    pass


def is_actual_dealer(connection):
    current_dealer = connection.get(DEALER_KEY)
    if current_dealer:
        if current_dealer.decode('utf-8') == APP_ID:
            return True
        else:
            return False
    logger.info('App with {id} is new dealer'.format(id=APP_ID))
    return True


def set_as_current_dealer(connection):
    with connection.pipeline() as pipe:
        while True:
            try:
                pipe.watch(DEALER_KEY)
                pipe.multi()
                pipe.set(DEALER_KEY, APP_ID, ex=1)
                pipe.execute()
                break
            except WatchError:
                return False
            finally:
                pipe.reset()
    return True

def send_message(connection):
    message = get_random_string(30)
    key = APP_ID + get_random_string(5)
    try:
        connection.set(key, message)
    except:
        logger.error('App with {id} can\'t create key \"{key}\" with message \"{msg}\"'.format(id=APP_ID,
                                                                                               key=key,
                                                                                               msg=message))
    else:
        logger.info('App with {id} created key \"{key}\" with message \"{msg}\"'.format(id=APP_ID,
                                                                                        key=key,
                                                                                        msg=message))

if __name__ == "__main__":
    connection = get_redis_connect()
    while True:
        if is_actual_dealer(connection):
            if set_as_current_dealer(connection):
                send_message(connection)
                sleep(0.5)
        # else
            #read random key
            #delete random key
            #commit
