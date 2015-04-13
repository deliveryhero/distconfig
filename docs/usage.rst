Usage
=====

Example using zookeeper as a backend ::

    import kazoo

    from distconfig import Proxy

    client = kazoo.Client()

    proxy = Proxy.configure(
        'distconfig.backends.zookeeper.ZooKeeperBackend',
        client=client,
    )

    # config is a read only mapping-like object.
    config = proxy.get_config('/distconfig/service_name/config')

    print config['key']

    # Getting nested values works by supplying dotted key, this of course
    # mean that key cannot have a dot in them.
    print config['key.inner']

    # You can assert key value type by using typed get function e.g.
    # get_int, get_float, get_unicode, get_bytes ... .
    print config.get_int('key.inner.int_key')

    # Getting a inner config.
    print config.get_config('key.inner.dict_key')

