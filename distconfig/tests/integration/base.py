import abc
import json
import os
import time
import unittest

import six

envvar = 'DISTCONFIG_RUN_INTEGRATION_TEST'
if os.environ.get(envvar) != 'true':
    raise unittest.SkipTest('Skipping integration tests, to enable run: export %s=true' % envvar)


@six.add_metaclass(abc.ABCMeta)
class _BackendTestCase(unittest.TestCase):

    def setUp(self):
        super(_BackendTestCase, self).setUp()
        self.initial_config = {
            'string': 'foobar',
            'integer': 1,
            'float': 1.5,
            'boolean': False,
            'none': None
        }

    @abc.abstractproperty
    def path(self):
        pass

    @abc.abstractproperty
    def proxy(self):
        pass

    @abc.abstractmethod
    def create_config(self, value):
        pass

    @abc.abstractmethod
    def update_config(self, new_value):
        pass

    @abc.abstractmethod
    def delete_config(self):
        pass

    def serialize_config(self, config):
        return json.dumps(config).encode('utf8')

    def wait_for_backend_changes(self, timeout=5):
        config_value = None

        def callback(new_value):
            config_value = new_value  # noqa

        self.proxy.backend.add_listener(callback)

        start = time.time()
        while config_value is None and (time.time() - start) < timeout:
            time.sleep(1)

    def test_get_config(self):
        self.create_config(self.initial_config)

        config = self.proxy.get_config(self.path)

        self.assertDictEqual(config._data, self.initial_config)

    def test_get_unexistant_config(self):
        config = self.proxy.get_config('unexistant-path')

        self.assertDictEqual(config._data, {})

    def test_get_changed_config(self):
        self.create_config(self.initial_config)

        config = self.proxy.get_config(self.path)

        new_config = {
            'new': 'config',
            'different': 'values',
        }
        self.update_config(new_config)

        self.wait_for_backend_changes()

        self.assertDictEqual(config._data, new_config)

    def test_get_deleted_config(self):
        self.create_config(self.initial_config)

        config = self.proxy.get_config(self.path)

        self.delete_config()

        self.wait_for_backend_changes()

        self.assertDictEqual(config._data, {})

    def test_get_changed_two_times_config(self):
        self.create_config(self.initial_config)

        config = self.proxy.get_config(self.path)

        self.update_config({
            'firstname': 'Mouad',
            'lastname': 'Benchchaoui',
        })

        self.update_config(self.initial_config)

        self.wait_for_backend_changes()

        self.assertDictEqual(config._data, self.initial_config)

    def test_delete_and_create_config(self):
        config = self.proxy.get_config(self.path)

        self.create_config(self.initial_config)

        self.wait_for_backend_changes()

        self.assertDictEqual(config._data, self.initial_config)
