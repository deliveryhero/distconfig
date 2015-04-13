import os
import unittest

from kazoo.client import KazooClient

from distconfig.tests.integration.base import _BackendTestCase
from distconfig.api import Proxy


ZK_ENDPOINT_IP = os.environ.get('ZOOKEEPER_ENDPOINT_IP', '127.0.0.1')
ZK_ENDPOINT_PORT = int(os.environ.get('ZOOKEEPER_ENDPOINT_PORT', 2181))


class ZookeeperBackendTest(_BackendTestCase):

    path = 'distconfig/testing/config'
    zk_endpoint = "%s:%s" % (ZK_ENDPOINT_IP, ZK_ENDPOINT_PORT)
    client = KazooClient(hosts=zk_endpoint)
    proxy = Proxy.configure(
        'distconfig.backends.zookeeper.ZooKeeperBackend',
        client=client,
    )

    def setUp(self):
        super(ZookeeperBackendTest, self).setUp()

        try:
            self.client.start(timeout=0.2)
        except self.client.handler.timeout_exception:
            raise unittest.SkipTest("Can't connect to ZooKeeper on %s" % self.zk_endpoint)

    def tearDown(self):
        super(ZookeeperBackendTest, self).tearDown()
        self.client.stop()
        self.client.close()

    def create_config(self, value):
        value = self.serialize_config(value)
        self.client.create(self.path, value=value, ephemeral=True, makepath=True)

    def update_config(self, new_value):
        new_value = self.serialize_config(new_value)
        self.client.set(self.path, new_value)

    def delete_config(self):
        self.client.delete(self.path)
