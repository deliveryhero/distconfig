import abc
import logging
import sys

import six
import ujson


LOGGER = logging.getLogger(__name__)


@six.add_metaclass(abc.ABCMeta)
class BaseBackend(object):
    """Base abstract backend class.

    Backend implementation should inherit and implement ``get_raw`` method.

    :param parser: Callable that accept a string and parse it, default: ``ujson.loads``.
    :param logger: :class:`logging.Logger`` instance.
    """

    def __init__(self, parser=ujson.loads, logger=LOGGER):
        self.__callbacks = []
        self.__parser = parser

        self._logger = logger

    @abc.abstractmethod
    def get_raw(self, path):
        """Get path value from backend as it is.

        :path: key in the backend.
        :return: path value as saved in backend or None if not found in backend.
        """

    def get(self, path):
        """Get parsed path value in backend.

        :path: key in the backend.
        :return: path value parsed.
        """
        data = self.get_raw(path)
        return self._parse_raw_data(data)

    def _parse_raw_data(self, data):
        if data is None:
            return {}
        return self.__parser(data)

    def add_listener(self, callback):
        """Add callback to be called when data change in the backend.

        If the same callback is added more than once, then it will be notified more than once.
        That is, no check is made to ensure uniqueness.

        :param callback: Callable that accept one argument the new data.
        """
        self.__callbacks.append(callback)

    def remove_listener(self, callback):
        """Remove previously added callback.

        If callback had been added more than once, then only the first occurrence will be removed.

        :param callback: Callable as with ``:meth: add_listener``.
        :raise ValueError: In case callback was not previously registered.
        """
        self.__callbacks.remove(callback)

    def _notify_listeners(self, value):
        self._logger.debug('Notify listeners of new value: %r', value)
        value = self._parse_raw_data(value)
        last_exc = None
        for callback in self.__callbacks:
            try:
                callback(value)
            except Exception:
                last_exc = sys.exc_info()
        if last_exc:
            self._logger.exception('Notify listeners raised an exception', exc_info=last_exc)
            try:
                raise last_exc
            finally:
                del last_exc
