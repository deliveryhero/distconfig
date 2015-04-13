import json
import unittest

import mock

from distconfig.backends import base


class FakeBackend(base.BaseBackend):

    def __init__(self, data, **kwargs):
        super(FakeBackend, self).__init__(**kwargs)
        self._data = data

    def get_raw(self, path):
        return self._data.get(path)


class BackendTestCase(unittest.TestCase):

    def setUp(self):
        self.value = {'foo': 'bar'}
        self.raw_value = json.dumps(self.value)
        self.backend = FakeBackend({
            '/some/path': self.raw_value
        })

    def test_backend_get(self):
        self.assertEqual(self.backend.get('/some/path'), self.value)

    def test_backend_get_unexistant_path(self):
        self.assertEqual(self.backend.get('/no/existing/path'), {})

    def test_add_listeners(self):
        callback = mock.Mock(return_value=None)
        self.backend.add_listener(callback)

        self.backend._notify_listeners(self.raw_value)

        callback.assert_called_once_with(self.value)

    def test_add_multiple_listeners(self):
        callback1 = mock.Mock(return_value=None)
        self.backend.add_listener(callback1)

        callback2 = mock.Mock(return_value=None)
        self.backend.add_listener(callback2)

        self.backend._notify_listeners(self.raw_value)

        callback1.assert_called_once_with(self.value)
        callback2.assert_called_once_with(self.value)

    def test_add_listeners_multiple_time(self):
        callback = mock.Mock(return_value=None)
        self.backend.add_listener(callback)
        self.backend.add_listener(callback)
        self.backend.add_listener(callback)

        self.backend._notify_listeners(self.raw_value)

        self.assertEqual(callback.call_count, 3)
        callback.assert_called_with(self.value)

    def test_remove_listeners(self):
        callback = mock.Mock(return_value=None)
        self.backend.add_listener(callback)

        self.backend.remove_listener(callback)

        self.backend._notify_listeners(self.raw_value)

        self.assertEqual(callback.call_count, 0)

    def test_remove_listeners_multiple_time(self):
        callback = mock.Mock(return_value=None)
        self.backend.add_listener(callback)
        self.backend.add_listener(callback)
        self.backend.add_listener(callback)

        self.backend.remove_listener(callback)
        self.backend.remove_listener(callback)
        self.backend.remove_listener(callback)

        self.backend._notify_listeners(self.raw_value)

        self.assertEqual(callback.call_count, 0)

    def test_remove_listeners_multiple_time_keeping_others(self):
        callback = mock.Mock(return_value=None)
        self.backend.add_listener(callback)
        self.backend.add_listener(callback)
        self.backend.add_listener(callback)

        self.backend.remove_listener(callback)

        self.backend._notify_listeners(self.raw_value)

        self.assertEqual(callback.call_count, 2)

    def test_remove_listeners_more_than_you_should(self):
        callback = mock.Mock(return_value=None)
        self.backend.add_listener(callback)

        self.backend.remove_listener(callback)

        with self.assertRaises(ValueError):
            self.backend.remove_listener(callback)

    def test_listener_exception(self):
        callback = mock.Mock(side_effect=Exception('foo'))
        self.backend.add_listener(callback)

        with self.assertRaises(Exception):
            self.backend._notify_listeners(self.raw_value)

    def test_listener_log_exception_on_error(self):
        logger_mock = mock.Mock()

        backend = FakeBackend(
            {'/some/path': self.raw_value},
            logger=logger_mock)

        callback = mock.Mock(side_effect=Exception('foo'))
        backend.add_listener(callback)

        with self.assertRaises(Exception):
            backend._notify_listeners(self.raw_value)

        self.assertTrue(logger_mock.exception.called)
