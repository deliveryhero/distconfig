# -*- encoding: utf8 -*-
import six

import unittest

from distconfig.config import Config


class ConfigTestCase(unittest.TestCase):

    def setUp(self):
        self.test_data = {
            'inner': {
                'integer': 1,
                'float': 1.4,
                'boolean': True,
                'unicode': u'Straße',
                'bytes': six.b('bytes')
            },
            'outer': 'foobar',
            'esca/ped': 'escaped'
        }
        self.config = Config(self.test_data)

    def test_config_wrong_type(self):
        with self.assertRaises(TypeError):
            Config('foobar')

    def test_itemgetter(self):
        self.assertEqual(self.config['outer'], 'foobar')

    def test_get(self):
        self.assertEqual(self.config.get('outer'), 'foobar')

    def test_get_default(self):
        value = self.config.get('inner/noexistant', 'foobar')
        self.assertEqual(value, 'foobar')

    def test_get_escaped_key(self):
        value = self.config.get('esca\/ped')
        self.assertEqual(value, 'escaped')

    def test_no_key_exception(self):
        with self.assertRaisesRegexp(KeyError, "No key 'unexistant' under path 'inner.boolean'"):
            self.config['inner/boolean/unexistant']

    def test_config_len(self):
        self.assertEqual(len(self.config), 3)

    def test_config_iter(self):
        self.assertEqual(sorted(self.config), ['esca/ped', 'inner', 'outer'])

    def test_contains_path(self):
        self.assertTrue('inner/unicode' in self.config)
        self.assertTrue('outer' in self.config)

        self.assertTrue('inner/not_there' not in self.config)

    def test_config_str(self):
        self.assertEqual(str(self.config), 'Config(%r)' % self.test_data)

    def test_get_config(self):
        inner_config = self.config.get_config('inner')

        self.assertEqual(inner_config, Config(self.test_data['inner']))

    def test_get_config_with_default(self):
        self.assertEqual(self.config.get_config('inner/not_there', default={}), Config({}))

    def test_get_config_wrong_type(self):
        with self.assertRaises(TypeError):
            self.config.get_config('outer')

        with self.assertRaises(TypeError):
            self.config.get_config('inner/not_there', default=1)

    def test_get_int(self):
        self.assertEqual(self.config.get_int('inner/integer'), 1)

    def test_get_int_with_default(self):
        self.assertEqual(self.config.get_int('inner/not_there', default=1), 1)

    def test_get_int_wrong_type(self):
        with self.assertRaises(TypeError):
            self.config.get_int('outer')

        with self.assertRaises(TypeError):
            self.config.get_int('inner/not_there', default='wrong_type')

    def test_get_float(self):
        self.assertEqual(self.config.get_float('inner/float'), 1.4)

    def test_get_float_with_default(self):
        self.assertEqual(self.config.get_float('inner/not_there', default=2.1), 2.1)

    def test_get_float_wrong_type(self):
        with self.assertRaises(TypeError):
            self.config.get_float('outer')

        with self.assertRaises(TypeError):
            self.config.get_float('inner/not_there', default=False)

    def test_get_bool(self):
        self.assertEqual(self.config.get_boolean('inner/boolean'), True)

    def test_get_bool_with_default(self):
        self.assertEqual(self.config.get_boolean('inner/not_there', default=False), False)

    def test_get_boolean_wrong_type(self):
        with self.assertRaises(TypeError):
            self.config.get_boolean('outer')

        with self.assertRaises(TypeError):
            self.config.get_boolean('inner/not_there', default='wrong type')

    def test_get_unicode(self):
        self.assertEqual(self.config.get_unicode('inner/unicode'), u'Straße')

    def test_get_unicode_with_default(self):
        self.assertEqual(self.config.get_unicode('inner/not_there', default=u''), u'')

    def test_get_unicode_wrong_type(self):
        with self.assertRaises(TypeError):
            self.config.get_unicode('inner/integer')

        with self.assertRaises(TypeError):
            self.config.get_unicode('inner/not_there', default=1)

    def test_get_bytes(self):
        self.assertEqual(self.config.get_bytes('inner/bytes'), six.b('bytes'))

    def test_get_bytes_with_default(self):
        self.assertEqual(self.config.get_bytes('inner/not_there', default=six.b('')), b'')

    def test_get_bytes_wrong_type(self):
        with self.assertRaises(TypeError):
            self.config.get_bytes('inner/unicode')

        with self.assertRaises(TypeError):
            self.config.get_bytes('inner/not_there', default=1)


class InnerConfigTestCase(unittest.TestCase):

    def setUp(self):
        self.test_data = {
            'inner': {
                'foo': 'bar',
                'subinner': {
                    'baz': 'taz'
                }
            },
            'another_inner': {
                'foobar': 'wat?'
            }
        }
        self.config = Config(self.test_data)

    def test_inner_config_update(self):
        inner_config = self.config.get_config('inner')
        self.config._invalidate({
            'inner': {
                'integer': 5
            }
        })

        self.assertEqual(inner_config.get('integer'), 5)

    def test_two_inners_update(self):
        inner = self.config.get_config('inner')
        another_inner = self.config.get_config('another_inner')

        self.config._invalidate({
            'inner': {}
        })

        self.assertEqual(inner._data, {})
        self.assertEqual(another_inner._data, {})

    def test_nested_inner_config_update(self):
        inner = self.config.get_config('inner')
        subinner = self.config.get_config('inner/subinner')

        self.config._invalidate({
            'inner': {
                'new': 'yay',
                'subinner': {
                    'subnew': 'subyay'
                }
            }
        })

        self.assertEqual(inner.get('new'), 'yay')
        self.assertEqual(inner.get('subinner/subnew'), 'subyay')
        self.assertEqual(subinner.get('subnew'), 'subyay')

    def test_identity_inner_config(self):
        inner1 = self.config.get_config('inner')
        inner2 = self.config.get_config('inner')

        self.assertIs(inner1, inner2)
