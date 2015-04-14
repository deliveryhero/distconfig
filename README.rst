.. image:: https://travis-ci.org/deliveryhero/distconfig.svg?branch=master
  :target: https://travis-ci.org/deliveryhero/distconfig

.. image:: https://readthedocs.org/projects/distconfig/badge/?version=latest
  :target: https://readthedocs.org/projects/distconfig/?badge=latest
  :alt: Documentation Status

distconfig
==========

Library to manage distributed configuration using either `ZooKeeper <https://zookeeper.apache.org/>`_ or
`Etcd <https://github.com/coreos/etcd>`_ or `Consul <http://www.consul.io/>`_.

Rational
--------

When you have to manage configuration of a given services that are distributed across nodes, you may want
to consider using either one of the distributed configuration managers e.g. zookeeper, etcd, consul ..., this
library goal is to give developers an easy access to configuration stored in the previous backends.

Installation:
-------------

To use **ZooKeeper** as backend you should install ``distconfig`` using ::

    $ pip install distconfig[zookeeper]

with **etcd**::

    $ pip install distconfig[etcd]

with **consul**::

    $ pip install distconfig[consul]

Usage:
------

Example using zookeeper as a backend ::

    from kazoo import client

    from distconfig import Proxy

    client = client.KazooClient()
    # The user must call ``KazooClient.start()`` before using this particular
    # backend
    client.start()

    proxy = Proxy.configure(
        'distconfig.backends.zookeeper.ZooKeeperBackend',
        client=client,
    )

    # config is a read only mapping-like object.
    config = proxy.get_config('/distconfig/service_name/config')

    print config['key']

    # Getting nested values works by supplying key seperated by '/' char.
    print config['key/inner']

    # You can assert key value type by using typed get function e.g.
    # get_int, get_float, get_unicode, get_bytes ... .
    print config.get_int('key/inner/int_key')

    # Getting a inner config.
    print config.get_config('key/inner/dict_key')


Development:
------------

Start by installing dependencies ::

    $ pip install -r requirements/dev.txt requirements/base.txt

To run unit test use tox ::

    $ tox

To run integration test, we recommend you to install `docker <https://www.docker.com/>`_ and then run ::

    $ ./run-tests.sh

The above script will setup docker container for each of the backend
and run the integration tests on them.


TODO:
-----

- Add file as a backend (use https://pypi.python.org/pypi/watchdog)
