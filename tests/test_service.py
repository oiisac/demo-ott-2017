import time
import unittest
from unittest.mock import patch


from service.util import get_redis_connect
from service.main import (clean_db, set_as_dealer, send_message, read_message,
                          DEALER_KEY, APP_ID, DEALER_KEY_TTL, MESSAGE_KEY_PFX, ERROR_KEY_PFX)


class TestEndpoints(unittest.TestCase):

    def setUp(self):
        self.connection = get_redis_connect()

    def tearDown(self):
        clean_db(self.connection)

    def test_set_as_dealer(self):
        init_value = self.connection.get(DEALER_KEY)
        set_as_dealer(self.connection)
        result_value = self.connection.get(DEALER_KEY).decode('utf-8')
        time.sleep(DEALER_KEY_TTL)
        end_value = self.connection.get(DEALER_KEY)

        self.assertEqual(init_value, None)
        self.assertEqual(result_value, APP_ID)
        self.assertEqual(end_value, None)

    def test_send_message(self):
        send_message(self.connection)
        result = self.connection.scan(match=MESSAGE_KEY_PFX + '*')
        self.assertIsInstance(result, tuple)
        self.assertNotEqual(result, [])
        self.assertIsInstance(result[1], list)
        self.assertIsInstance(result[1][0], bytes)

    @patch('service.util.get_succes_chance')
    def test_read_message(self, mock_get_succes_chance):
        mock_get_succes_chance.return_value = True
        send_message(self.connection)
        result = self.connection.scan(match=MESSAGE_KEY_PFX + '*')
        self.assertIsInstance(result[1][0], bytes)
        read_message(self.connection)
        result = self.connection.get(result[1][0])
        self.assertEqual(result, None)

    @patch('service.util.get_succes_chance')
    def test_read_error_message(self, mock_get_succes_chance):
        mock_get_succes_chance.return_value = False
        send_message(self.connection)
        result = self.connection.scan(match=MESSAGE_KEY_PFX + '*')
        self.assertIsInstance(result[1][0], bytes)
        value = self.connection.get(result[1][0])
        read_message(self.connection)
        result = self.connection.scan(match=ERROR_KEY_PFX + '*')
        self.assertIsInstance(result[1][0], bytes)
