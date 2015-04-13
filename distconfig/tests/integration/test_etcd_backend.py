import os
import socket
import unittest

import etcd
from six.moves import http_client

from distconfig.tests.integration.base import _BackendTestCase
from distconfig.api import Proxy


EPHEMERAL_TEST_DATA_TTL = 60
ETCD_ENDPOINT_IP = os.environ.get('ETCD_ENDPOINT_IP', '127.0.0.1')
ETCD_ENDPOINT_PORT = int(os.environ.get('ETCD_ENDPOINT_PORT', 4001))


def etcd_running():
    conn = http_client.HTTPConnection(ETCD_ENDPOINT_IP, port=ETCD_ENDPOINT_PORT)
    try:
        conn.request('HEAD', '/')
    except (socket.error, socket.gaierror):
        return False
    else:
        return True


@unittest.skipUnless(etcd_running(), "Can't connect to Etcd on %s:%s" % (ETCD_ENDPOINT_IP, ETCD_ENDPOINT_PORT))
class EtcdBackendTest(_BackendTestCase):

    path = 'distconfig/testing/config'
    client = etcd.Client(ETCD_ENDPOINT_IP, ETCD_ENDPOINT_PORT)
    proxy = Proxy.configure(
        'distconfig.backends.etcd.EtcdBackend',
        client=client,
    )

    def tearDown(self):
        super(EtcdBackendTest, self).tearDown()
        try:
            self.client.delete(self.path)
        except etcd.EtcdKeyNotFound:
            pass

    def create_config(self, value):
        value = self.serialize_config(value)
        self.client.set(self.path, value, ttl=EPHEMERAL_TEST_DATA_TTL)

    def update_config(self, new_value):
        new_value = self.serialize_config(new_value)
        self.client.set(self.path, new_value, ttl=EPHEMERAL_TEST_DATA_TTL)

    def delete_config(self):
        self.client.delete(self.path)
