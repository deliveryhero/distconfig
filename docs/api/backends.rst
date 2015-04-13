Backends
========


Base class
----------

.. automodule:: distconfig.backends.base

.. autoclass:: BaseBackend
   :members:


Existing backends
-----------------

The current backends exist out of the box:

.. automodule:: distconfig.backends.zookeeper

.. autoclass:: ZooKeeperBackend
   :members:


.. automodule:: distconfig.backends.consul

.. autoclass:: ConsulBackend
   :members:


.. automodule:: distconfig.backends.etcd

.. autoclass:: EtcdBackend
   :members:


Execution Contexts
------------------

.. automodule:: distconfig.backends.execution_context

.. autoclass:: GeventExecutionContext
   :members:

.. autoclass:: ThreadingExecutionContext
   :members:
