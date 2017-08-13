import argparse
import logging
from time import sleep

from redis.exceptions import WatchError

from app import APP_NAME
from app import util


APP_ID = util.get_random_string(5)
DEALER_KEY = 'dealer'
MESSAGE_KEY_PFX = 'msg'
ERROR_KEY_PFX = 'err'

SLEEP_TIME = 0.5  # in seconds
DEALER_KEY_TTL = int(SLEEP_TIME * 2) # in seconds


logger = logging.getLogger('{app}_{id}'.format(app=APP_NAME, id=APP_ID))
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


def set_as_dealer(connection):
    with connection.pipeline() as pipe:
        pipe.watch(DEALER_KEY)
        current_dealer = pipe.get(DEALER_KEY)
        if current_dealer:
            if current_dealer.decode('utf-8') == APP_ID:
                pipe.set(DEALER_KEY, APP_ID, ex=DEALER_KEY_TTL)
        else:
            pipe.set(DEALER_KEY, APP_ID, ex=DEALER_KEY_TTL)
            logger.info('App with id {id} is new dealer'.format(id=APP_ID))
        pipe.watch(DEALER_KEY)
        new_dealer = pipe.get(DEALER_KEY)
        pipe.execute()
    return new_dealer.decode('utf-8') == APP_ID


def send_message(connection):
    message = util.get_random_string(30)
    key = '{pfx}_{time}_{app}'.format(pfx=MESSAGE_KEY_PFX, time=util.get_time_in_ms(), app=APP_ID)
    try:
        connection.setnx(key, message)
    except:
        logger.error('App with id {id} can\'t create key \"{key}\" with message \"{msg}\"'\
            .format(id=APP_ID, key=key, msg=message))
    else:
        logger.info('App with id {id} created key \"{key}\" with message \"{msg}\"'\
            .format(id=APP_ID, key=key, msg=message))


def read_message(connection):
    succes = util.get_succes_chance()
    message = ''
    with connection.pipeline() as pipe:
        key = connection.scan_iter(match=MESSAGE_KEY_PFX + '*').__next__()
        if key:
            key_name = key.decode('utf-8')
            try:
                pipe.watch(key_name)
                message = pipe.get(key_name).decode('utf-8')
                pipe.multi()
                if succes:
                    pipe.delete(key_name)
                else:
                    new_key_name = key_name.replace(MESSAGE_KEY_PFX, ERROR_KEY_PFX)
                    pipe.rename(key_name, new_key_name)
                result = pipe.execute()

            except WatchError:
                logger.error('Key \"{key}\" with message \"{msg}\" reused by other client'\
                    .format(key=key_name, msg=message))

            if succes:
                logger.info('App with id {id} read key \"{key}\" with message \"{msg}\"'\
                    .format(id=APP_ID, key=key_name, msg=message))
            else:
                logger.warning('App with id {id} read key \"{key}\" with malformed message \"{msg}\"'\
                    .format(id=APP_ID, key=key_name, msg=message))


def read_erros(connection):
    keys = connection.scan_iter(match=ERROR_KEY_PFX + '*')
    with connection.pipeline() as pipe:
        for key in keys:
            if pipe.watch(key):
                print(pipe.get(key).decode('utf-8'))
            pipe.delete(key)
        pipe.execute()


def clean_db(connection):
    connection.flushdb()
    print('All keys deleted.')


if __name__ == "__main__":
    connection = util.get_redis_connect()

    parser = argparse.ArgumentParser(description='Read/write value with redis DB')
    parser.add_argument('--getErrors', help='Get all erorrs from DB, print on screen and exit',
                        required=False, action='store_true')
    parser.add_argument('--clean', help='Clean all keys in DB and exit', required=False, action='store_true')

    args = parser.parse_args()

    if util.is_errors_request(args.getErrors):
        read_erros(connection)
    elif util.is_clean_request(args.clean):
        clean_db(connection)
    else:
        while True:
            if set_as_dealer(connection):
                send_message(connection)
            else:
                read_message(connection)
            sleep(0.5)
