import os

PACKAGE_VERSION = "0.1.0"
APP_NAME = 'demo_task_for_ott'

REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
REDIS_PORT = 6379
REDIS_DB = 0
