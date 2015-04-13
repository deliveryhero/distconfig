

def resolve_dotted_name(name):
    """Return object referenced by dotted name.

    :param name: dotted name as a String.
    :return: Resolved Python object.
    :raises ImportError: If can't resolve ``nane``

    Examples:

        >>> resolve_dotted_name('sys.exit')
        <built-in function exit>
        >>> resolve_dotted_name('xml.etree.ElementTree')  # doctest: +ELLIPSIS
        <module 'xml.etree.ElementTree' ...>
        >>> resolve_dotted_name('distconfig.backends.zookeeper.ZooKeeperBackend')
        <class 'distconfig.backends.zookeeper.ZooKeeperBackend'>

    """
    paths = name.split('.')
    current = paths[0]
    found = __import__(current)
    for part in paths[1:]:
        current += '.' + part
        try:
            found = getattr(found, part)
        except AttributeError:
            found = __import__(current, fromlist=part)
    return found
