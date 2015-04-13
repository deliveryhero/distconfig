import abc
import threading

import six


@six.add_metaclass(abc.ABCMeta)
class ExecutionContext(object):
    """Base abstract execution context class."""

    @abc.abstractmethod
    def run(self, func, *args, **kwargs):
        pass


class GeventExecutionContext(ExecutionContext):
    """Execution context that run background function as a Greenlet.

    gevent monkey patching must be done by user.
    """

    def run(self, func, *args, **kwargs):
        """Run given function in a Greenlet."""
        import gevent

        gevent.spawn(func, *args, **kwargs)
        gevent.sleep()


class ThreadingExecutionContext(ExecutionContext):
    """Execution context that run background function as a OS Thread."""

    def run(self, func, *args, **kwargs):
        """Run given function in a daemon OS thread."""
        thread = threading.Thread(target=func, args=args, kwargs=kwargs)
        thread.daemon = True
        thread.start()
