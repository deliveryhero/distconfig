import os
import socket
import unittest

import consul
from six.moves import http_client

from distconfig.tests.integration.base import _BackendTestCase
from distconfig.api import Proxy


CONSUL_ENDPOINT_IP = os.environ.get('CONSUL_ENDPOINT_IP', '127.0.0.1')
CONSUL_ENDPOINT_PORT = int(os.environ.get('CONSUL_ENDPOINT_PORT', 8500))


def consul_running():
    conn = http_client.HTTPConnection(CONSUL_ENDPOINT_IP, port=CONSUL_ENDPOINT_PORT)
    try:
        conn.request('HEAD', '/')
    except (socket.error, socket.gaierror):
        return False
    else:
        return True


@unittest.skipUnless(consul_running(), "Can't connect to Consul on %s:%s" % (CONSUL_ENDPOINT_IP, CONSUL_ENDPOINT_PORT))
class ConsulBackendTest(_BackendTestCase):

    path = 'distconfig/testing/config'
    client = consul.Consul(CONSUL_ENDPOINT_IP, CONSUL_ENDPOINT_PORT)
    proxy = Proxy.configure(
        'distconfig.backends.consul.ConsulBackend',
        client=client
    )

    def setUp(self):
        super(ConsulBackendTest, self).setUp()
        self.client = consul.Consul(CONSUL_ENDPOINT_IP, CONSUL_ENDPOINT_PORT)

    def tearDown(self):
        super(ConsulBackendTest, self).tearDown()
        try:
            self.client.kv.delete(self.path)
        except KeyError:
            pass

    def create_config(self, value):
        value = self.serialize_config(value)
        self.client.kv.put(self.path, value)

    def update_config(self, new_value):
        new_value = self.serialize_config(new_value)
        self.client.kv.put(self.path, new_value)

    def delete_config(self):
        self.client.kv.delete(self.path)
