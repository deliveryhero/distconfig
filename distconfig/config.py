import collections
import functools
import re
import weakref

import six


UNDEFINED = object()


def _split_path(path, _regex=re.compile(r'(?<!\\)/')):
    """
    Example:

        >>> _split_path('a/b/c')
        ['a', 'b', 'c']
        >>> _split_path('a/b/c/')
        ['a', 'b', 'c', '']
        >>> _split_path('/a/b/c')
        ['', 'a', 'b', 'c']
        >>> _split_path('//')
        ['', '', '']
        >>> _split_path('a\/b/c')
        ['a/b', 'c']

    """
    return list(map(functools.partial(re.sub, r'\\/', '/'), _regex.split(path)))


class Config(collections.Mapping):
    """Read only mapping-like for holding configuration.

    Note: At the opposite of ``ConfigParser.RawConfigParser`` in stdlib, methods
    like ``get_<type>`` in this class do **not** coerse, instead the use case
    is type assertion, i.e. When a user call ``Config.get_int`` on a key where
    the value is a string e.g. '2', the call will fail with a ``TypeError``.

    """

    def __init__(self, data):
        if not isinstance(data, collections.Mapping):
            raise TypeError('Need a mapping-like object, instead got %r' % type(data))
        self._data = data
        self.__inner_configs = weakref.WeakValueDictionary()

    def __str__(self):
        return '%s(%r)' % (self.__class__.__name__, self._data)

    def _invalidate(self, new_data):
        self._data = new_data
        for path, inner_config in six.iteritems(self.__inner_configs):
            inner_data = self.get(path, default={})
            inner_config._invalidate(inner_data)

    def __iter__(self):
        return iter(self._data)

    def __len__(self):
        return len(self._data)

    def __getitem__(self, path):
        data = self._data
        keys = _split_path(path)
        for i, key in enumerate(keys):
            try:
                data = data[key]
            except (KeyError, TypeError):
                raise KeyError('No key %r under path %r' % (key, '.'.join(keys[:i])))
        return data

    def get(self, path, default=None, type_=None):
        """Same as ``dict.get(k[,d])`` with an extra argument ``type_`` that assert
        type matching if given.

        ``path`` argument can be in the form 'key1/key2/key3' as a shortcut for doing
        ``config['key1']['key2']['key3']``. In case a key have a / in it, we can escape it
        like so 'key1\/key2/key3' this will be translated to ``config['key1/key2']['key3']``

        :param path: path expression e.g. 'key1/key2/key3'
        :param default: default value to return when key is missing, in case it's
            supplied ``default`` with ``type_``, ``default`` must be of of type ``type_``,
            default: None.
        :param type_: Python type to validate returned value, default: None.

        :return: the value of the requested path as a string.

        :raises TypeError: if path value is not of type ``type_``.
        :raises KeyError: if path doesn't exist and ``default`` is set to ``distconfig.config.UNDEFINED``.
        """
        if default is UNDEFINED:
            result = self[path]
        else:
            result = super(Config, self).get(path, default=default)
        if type_ and not isinstance(result, type_):
            raise TypeError('%r not of type %r' % (result, type_))
        return result

    def get_config(self, path, default=UNDEFINED):
        """Get path value as :class:`Config`.

        :param path: path expression e.g. 'key1.key2.key3'
        :param default: default value to return when key is missing,
            if supplied ``default`` must be of type dict, default: UNDEFINED.

        :return: the value of the requested path as a :class:`Config` instance.

        :raises TypeError: if path value is not of type ``type_``.
        :raises KeyError: if path doesn't exist and no default was given.
        """
        try:
            instance = self.__inner_configs[path]
        except KeyError:
            inner = self.get(path, default=default, type_=dict)
            instance = self.__inner_configs[path] = Config(inner)
        return instance

    def get_int(self, path, default=UNDEFINED):
        """Get path value as integer.

        :param path: path expression e.g. 'key1.key2.key3'
        :param default: default value to return when key is missing,
            if supplied ``default`` must be of type integer, default: UNDEFINED.

        :return: the value of the requested path as a Integer.

        :raises TypeError: if path value is not of type ``type_``.
        :raises KeyError: if path doesn't exist and no default was given.
        """
        return self.get(path, default=default, type_=int)

    def get_float(self, path, default=UNDEFINED):
        """Get path value as float.

        :param path: path expression e.g. 'key1.key2.key3'
        :param default: default value to return when key is missing,
            if supplied ``default`` must be of type float, default: UNDEFINED.

        :return: the value of the requested path as a Float.

        :raises TypeError: if path value is not of type ``type_``.
        :raises KeyError: if path doesn't exist and no default was given.
        """
        return self.get(path, default=default, type_=float)

    def get_boolean(self, path, default=UNDEFINED):
        """Get path value as boolean.

        :param path: path expression e.g. 'key1.key2.key3'
        :param default: default value to return when key is missing,
            if supplied ``default`` must be of type boolean, default: UNDEFINED.

        :return: the value of the requested path as a Boolean.

        :raises TypeError: if path value is not of type ``type_``.
        :raises KeyError: if path doesn't exist and no default was given.
        """
        return self.get(path, default=default, type_=bool)

    def get_unicode(self, path, default=UNDEFINED):
        """Get path value as unicode.

        :param path: path expression e.g. 'key1.key2.key3'
        :param default: default value to return when key is missing,
            if supplied ``default`` must be of type unicode, default: UNDEFINED.

        :return: the value of the requested path as a Unicode.

        :raises TypeError: if path value is not of type ``type_``.
        :raises KeyError: if path doesn't exist and no default was given.
        """
        return self.get(path, default=default, type_=six.text_type)

    def get_bytes(self, path, default=UNDEFINED):
        """Get path value as bytes.

        :param path: path expression e.g. 'key1.key2.key3'
        :param default: default value to return when key is missing,
            if supplied ``default`` must be of type bytes, default: UNDEFINED.

        :return: the value of the requested path as a Unicode.

        :raises TypeError: if path value is not of type ``type_``.
        :raises KeyError: if path doesn't exist and no default was given.
        """
        return self.get(path, default=default, type_=six.binary_type)


