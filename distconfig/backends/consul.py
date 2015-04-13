from distconfig.backends.base import BaseBackend
from distconfig.backends.execution_context import ThreadingExecutionContext


class ConsulBackend(BaseBackend):
    """Consul backend implementation.

    :param client: Instance of :class:`consul.Consul`.
    :param execution_context: Instance of :class:`distconfig.backends.execution_context.ExecutionContext`

    """

    def __init__(self, client, execution_context=ThreadingExecutionContext(), **kwargs):
        super(ConsulBackend, self).__init__(**kwargs)
        self._client = client
        self._execution_context = execution_context
        self._watching = set()

    def get_raw(self, key):
        result = self._get_backend_data(key)
        self._add_watcher(key)
        return result

    def _get_backend_data(self, key):
        _, result = self._client.kv.get(key)
        if result:
            result = result['Value']
        return result

    def _add_watcher(self, key):
        if key not in self._watching:
            self._watching.add(key)
            self._execution_context.run(self._watch_for_changes, key)

    def _watch_for_changes(self, key):
        index = None
        while 1:
            try:
                index, data = self._client.kv.get(key, index=index)
            except Exception as ex:
                self._logger.error('exception raised while listening on consul changes (re-launching watcher): %s', ex)
            else:
                if data:
                    data = data['Value']
                self._notify_listeners(data)
