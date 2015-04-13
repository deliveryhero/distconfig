from functools import partial

from kazoo.exceptions import NoNodeError
from kazoo.protocol.states import EventType

from distconfig.backends.base import BaseBackend


class ZooKeeperBackend(BaseBackend):
    """Zooekeeper backend implentation.

    If you are using gevent, make sure that the kazoo client is setup to
    use gevent event handler e.g. ``KazooClient(..., handler=SequentialGeventHandler())``

    User must call ``KazooClient.start()`` before using the backend.

    :param client: Instance of :class:`kazoo.client.KazooClient`.

    """

    def __init__(self, client, **kwargs):
        super(ZooKeeperBackend, self).__init__(**kwargs)
        self._client = client

    def get_raw(self, path):
        try:
            return self._get_and_watch_path(path)
        except NoNodeError:
            return self._get_and_watch_unexistant_path(path)

    def _get_and_watch_unexistant_path(self, path):
        self._client.retry(self._client.exists, path, watch=partial(self._on_path_change, path))

    def _get_and_watch_path(self, path):
        data, _ = self._client.retry(self._client.get, path, watch=partial(self._on_path_change, path))
        return data

    def _on_path_change(self, path, event):
        # XXX: Before we could set the new watches the data may have changed already
        # in ZooKeeper backend, in that case we may have missed the notification.
        # AFAIK there is no easy way to work around this.
        # https://zookeeper.apache.org/doc/r3.1.2/zookeeperProgrammers.html#sc_WatchRememberThese
        if event.type == EventType.DELETED:
            data = self._get_and_watch_unexistant_path(path)
        else:
            data = self._get_and_watch_path(path)
        return super(ZooKeeperBackend, self)._notify_listeners(data)
