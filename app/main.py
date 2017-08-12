import argparse
import logging
from time import sleep

from redis.exceptions import WatchError

from app import APP_NAME
from app.util import get_random_string, get_redis_connect, get_succes_chance, is_errors_request


APP_ID = get_random_string(5)
DEALER_KEY = 'current_dealer'
DEALER_KEY_TTL = 1 # in seconds


logger = logging.getLogger('{app}_{id}'.format(app=APP_NAME, id=APP_ID))
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


def get_connect():
    pool = redis.ConnectionPool(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)
    r = redis.Redis(connection_pool=pool)
    return r

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
                pipe.set(DEALER_KEY, APP_ID, ex=DEALER_KEY_TTL)
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
        connection.setnx(key, message)
    except:
        logger.error('App with {id} can\'t create key \"{key}\" with message \"{msg}\"'.format(id=APP_ID,
                                                                                               key=key,
                                                                                               msg=message))
    else:
        logger.info('App with {id} created key \"{key}\" with message \"{msg}\"'.format(id=APP_ID,
                                                                                        key=key,
                                                                                        msg=message))

def read_message(connection, key=None):
    succes = get_succes_chance()
    if not key:
        key = connection.randomkey()
    if key:
        key_name = key.decode('utf-8')
        if key_name != DEALER_KEY and not key_name.startswith('err_'):
            with connection.pipeline() as pipe:
                while True:
                    try:
                        pipe.watch(key_name)
                        pipe.multi()
                        message = pipe.get(key_name)
                        if succes:
                            pipe.delete(key)
                        else:
                            pipe.rename(key_name, 'err_' + key_name)
                        result = pipe.execute()
                        break
                    except WatchError:
                        pass
                    finally:
                        pipe.reset()
            message = result[0].decode('utf-8')
            if succes:
                logger.info('App with {id} read key \"{key}\" with message \"{msg}\"'.format(id=APP_ID,
                                                                                             key=key_name,
                                                                                             msg=message))
            else:
                logger.warning('App with {id} read key \"{key}\" with malformed message \"{msg}\"'.format(id=APP_ID,
                                                                                                  key=key_name,
                                                                                                  msg=message))

def read_erros(connection):
    keys = connection.keys(pattern='err_*')
    if keys:
        print(*[msg.decode('utf-8') + '\n' for msg in connection.mget(keys)])
        [connection.delete(key) for key in keys]


if __name__ == "__main__":
    connection = get_redis_connect()

    parser = argparse.ArgumentParser(description='Read/write value with redis DB')
    parser.add_argument('--getErrors', help='Get all erorrs, print and exit', required=False)

    args = parser.parse_args()

    if is_errors_request(args.getErrors):
        read_erros(connection)
    else:
        while True:
            if is_actual_dealer(connection):
                if set_as_current_dealer(connection):
                    send_message(connection)
                    sleep(0.5)
            else:

                read_message(connection)