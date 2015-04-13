from . import config, utils


class Proxy(object):
    """Proxy class for differents backend."""

    def __init__(self, backend):
        self._backend = backend

    @property
    def backend(self):
        """Readonly property for backend."""
        return self._backend

    @classmethod
    def configure(cls, backend_qualname, **backend_options):
        """Configure backend.

        :param backend_qualname: Backend class qualifed name (dotted-name)
            e.g. ``distconfig.backends.zookeeper.ZooKeeperBackend``.
        :param logger: ``logging.Logger`` instance to use for logging.
        :param parser: Callable that accept the raw config data saved in
            the backend and should return the config data parsed,
            default: ``ujson.loads``.
        :param backend_options: Keyword arguments to pass to backend class.
        """
        backend_cls = utils.resolve_dotted_name(backend_qualname)
        backend = backend_cls(**backend_options)
        return cls(backend)

    def get_config(self, path, config_cls=config.Config):
        """Get configuration from path.

        :param path: Location of the configuratin in the backend.
        :param config_cls: configuration class to return, default: :class:`distconfig.config.Config`.
        :return: ``config_cls`` instance.

        """
        data = self._backend.get(path)
        config = config_cls(data)
        self._backend.add_listener(config._invalidate)
        return config
