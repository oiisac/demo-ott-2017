import os

from service import APP_NAME, PACKAGE_VERSION
from service.util import get_random_string


APP_ID = get_random_string(5)

REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
REDIS_PORT = 6379
REDIS_DB = 0

DEALER_KEY = 'dealer'
MESSAGE_KEY_PFX = 'msg'
ERROR_KEY_PFX = 'err'
LOCKED_KEY_PFX = 'lock'

SLEEP_TIME = 0.5  # in seconds
DEALER_KEY_TTL = int(SLEEP_TIME * 2) # in seconds

NETWORK = APP_NAME + '_network'
REDIS_CONT = REDIS_HOST
APP_IMG = APP_NAME
LOG_VOLUME = 'logs'
INST_NUMBER = 10
