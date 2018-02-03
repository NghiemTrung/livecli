.. _api:

API Reference
=============

.. module:: livecli

This ia reference of all the available API methods in Livecli.

Livecli
------------

.. autofunction:: streams


Session
-------

.. autoclass:: Livecli
    :members:


Plugins
-------
.. module:: livecli.plugin
.. autoclass:: Plugin
    :members:


Streams
-------

All streams inherit from the :class:`Stream` class.

.. module:: livecli.stream
.. autoclass:: Stream
    :members:


.. _api-stream-subclasses:

Stream subclasses
^^^^^^^^^^^^^^^^^

You are able to inspect the parameters used by each stream,
different properties are available depending on stream type.

.. autoclass:: AkamaiHDStream
    :members:

.. autoclass:: HDSStream
    :members:

.. autoclass:: HLSStream
    :members:

.. autoclass:: HTTPStream
    :members:

.. autoclass:: RTMPStream
    :members:


Exceptions
----------

Livecli has three types of exceptions:

.. autoexception:: livecli.LivecliError
.. autoexception:: livecli.PluginError
.. autoexception:: livecli.NoPluginError
.. autoexception:: livecli.StreamError
