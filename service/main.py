import argparse
import logging
from time import sleep

from redis.exceptions import WatchError, ResponseError

from service import util
from service.C import APP_ID, APP_NAME, DEALER_KEY, MESSAGE_KEY_PFX, ERROR_KEY_PFX, SLEEP_TIME, DEALER_KEY_TTL

logger_name = '{app}_{id}'.format(app=APP_NAME, id=APP_ID)
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[logging.FileHandler('/tmp/{app}/{name}.log'.format(name=logger_name, app= APP_NAME)),
                              logging.StreamHandler()])

logger = logging.getLogger(logger_name)


def set_as_dealer(connection):
    """ Set current app as message dealer if dealer not exist
        or update dealer key
    """
    with connection.pipeline() as pipe:
        pipe.watch(DEALER_KEY)
        current_dealer = pipe.get(DEALER_KEY)
        if current_dealer:
            if current_dealer.decode('utf-8') == APP_ID:
                pipe.set(DEALER_KEY, APP_ID, ex=DEALER_KEY_TTL)
        else:
            pipe.set(DEALER_KEY, APP_ID, ex=DEALER_KEY_TTL)
            logger.info('App with id {id} is new dealer'.format(id=APP_ID))
        pipe.execute()
    new_dealer = connection.get(DEALER_KEY) or b''
    return new_dealer.decode('utf-8') == APP_ID


def send_message(connection):
    """ Send message with random value to DB
    """
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
    """ Read message from DB and mark it with error key if succes == False
    """
    succes = util.get_succes_chance()
    message = ''
    try:
        key = connection.scan_iter(match=MESSAGE_KEY_PFX + '*').__next__()
    except:
        key = b''
    key_name = key.decode('utf-8')
    if key_name:
        if not util.is_key_locked(connection, key_name):
            if util.set_key_locked(connection, key_name):
                value = connection.get(key_name)
                if value:
                    message = value.decode('utf-8')
                if succes:
                    connection.delete(key_name)
                else:
                    new_key_name = key_name.replace(MESSAGE_KEY_PFX, ERROR_KEY_PFX)
                    result = connection.renamenx(key_name, new_key_name)
        if message:
            if succes:
                logger.info('App with id {id} read key \"{key}\" with message \"{msg}\"'\
                    .format(id=APP_ID, key=key_name, msg=message))
            else:
                logger.warning('App with id {id} read key \"{key}\" with malformed message \"{msg}\"'\
                    .format(id=APP_ID, key=key_name, msg=message))
            return True


def read_erros(connection):
    """ Read and delete all error messages from DB
    """
    keys = connection.scan_iter(match=ERROR_KEY_PFX + '*')
    with connection.pipeline() as pipe:
        for key in keys:
            if pipe.watch(key):
                print(pipe.get(key).decode('utf-8'))
            pipe.delete(key)
        pipe.execute()


def clean_db(connection):
    """ Clean DB
    """
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
                sleep(SLEEP_TIME)
            else:
                read_result = read_message(connection)
                if read_result:
                    sleep(SLEEP_TIME)
