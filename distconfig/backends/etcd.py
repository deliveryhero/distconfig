from __future__ import absolute_import

from etcd import EtcdKeyNotFound

from distconfig.backends.base import BaseBackend
from distconfig.backends.execution_context import ThreadingExecutionContext


class EtcdBackend(BaseBackend):
    """Etcd backend implementation.

    :param client: Instance of :class:`etcd.Client`.
    :param execution_context: Instance of :class:`distconfig.backends.execution_context.ExecutionContext`
    """

    def __init__(self, client, execution_context=ThreadingExecutionContext(), **kwargs):
        super(EtcdBackend, self).__init__(**kwargs)
        self._client = client
        self._execution_context = execution_context
        self._watching = set()

    def get_raw(self, key):
        result = self._get_backend_data(key)
        self._add_watcher(key)
        return result

    def _get_backend_data(self, key):
        try:
            result = self._client.get(key)
        except EtcdKeyNotFound:
            return
        else:
            return result.value

    def _add_watcher(self, key):
        if key not in self._watching:
            self._watching.add(key)
            self._execution_context.run(self._watch_for_changes, key)

    def _watch_for_changes(self, key):
        index = None
        while 1:
            try:
                response = self._client.watch(key, index=index)
            except Exception as ex:
                self._logger.error('exception raised while listening on etcd changes (re-launching watcher): %s', ex)
            else:
                if index is None:
                    index = response.etcd_index
                else:
                    index += 1
                self._notify_listeners(response.value)
