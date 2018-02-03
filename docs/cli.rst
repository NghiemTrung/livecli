.. _cli:

Command-Line Interface
======================

Tutorial
--------

Livecli is command-line application, this means the commands described
here should be typed into a terminal. On Windows this means you should open
the `command prompt`_ or `PowerShell`_, on Mac OS X open the `Terminal`_ app
and if you're on Linux or BSD you probably already know the drill.

The way Livecli works is that it's only a means to extract and transport
the streams, and the playback is done by an external video player. Livecli
works best with `VLC`_ or `mpv`_, which are also cross-platform, but other players
may be compatible too, see the :ref:`Players` page for a complete overview.

Now to get into actually using Livecli, let's say you want to watch the
stream located on http://twitch.tv/twitch, you start off by telling Livecli
where to attempt to extract streams from. This is done by giving the URL to the
command :command:`livecli` as the first argument:

.. code-block:: console

    $ livecli twitch.tv/twitch
    [cli][info] Found matching plugin twitch for URL twitch.tv/twitch
    Available streams: audio, high, low, medium, mobile (worst), source (best)


.. note::
    You don't need to include the protocol when dealing with HTTP URLs,
    e.g. just ``twitch.tv/twitch`` is enough and quicker to type.


This command will tell Livecli to attempt to extract streams from the URL
specified, and if it's successful, print out a list of available streams to choose
from.

In some cases  (`Supported streaming protocols`_)  local files are supported
using the ``file://`` protocol, for example a local HLS playlist can be played.
Relative file paths and absolute paths are supported. All path separators are ``/``,
even on Windows.

.. code-block:: console

    $ livecli hls://file://C:/hls/playlist.m3u8
    [cli][info] Found matching plugin stream for URL hls://file://C:/hls/playlist.m3u8
    Available streams: 180p (worst), 272p, 408p, 554p, 818p, 1744p (best)


To select a stream and start playback, we simply add the stream name as a second
argument to the :command:`livecli` command:

.. sourcecode:: console

    $ livecli twitch.tv/twitch source
    [cli][info] Found matching plugin twitch for URL twitch.tv/twitch
    [cli][info] Opening stream: source (hls)
    [cli][info] Starting player: vlc


The stream you chose should now be playing in the player. It's a common use case
to just want start the highest quality stream and not be bothered with what it's
named. To do this just specify ``best`` as the stream name and Livecli will
attempt to rank the streams and open the one of highest quality. You can also
specify ``worst`` to get the lowest quality.

Now that you have a basic grasp of how Livecli works, you may want to look
into customizing it to your own needs, such as:

- Creating a :ref:`configuration file <cli-liveclirc>` of options you
  want to use
- Setting up your player to :ref:`cache some data <issues-player_caching>`
  before playing the stream to help avoiding buffering issues


.. _command prompt: https://en.wikipedia.org/wiki/Command_Prompt
.. _PowerShell: https://www.microsoft.com/powershell
.. _Terminal: https://en.wikipedia.org/wiki/Terminal_(OS_X)
.. _VLC: https://www.videolan.org/
.. _mpv: https://mpv.io/


.. _cli-liveclirc:

Configuration file
------------------

Writing the command-line options every time is inconvenient, that's why Livecli
is capable of reading options from a configuration file instead.

Livecli will look for config files in different locations depending on
your platform:

================= ====================================================
Platform          Location
================= ====================================================
Unix-like (POSIX) - $XDG_CONFIG_HOME/livecli/config
                  - ~/.liveclirc
Windows           %APPDATA%\\livecli\\liveclirc
================= ====================================================

You can also specify the location yourself using the :option:`--config` option.

.. note::

  - `$XDG_CONFIG_HOME` is ``~/.config`` if it has not been overridden
  - `%APPDATA%` is usually ``<your user directory>\Application Data``

.. note::

  On Windows there is a default config created by the installer but on any
  other platform you must create the file yourself.


Syntax
^^^^^^

The config file is a simple text file and should contain one
:ref:`command-line option <cli-options>` (omitting the dashes) per
line in the format::

  option=value

or for a option without value::

  option

.. note::
    Any quotes used will be part of the value, so only use when the value needs them,
    e.g. specifying a player with a path containing spaces.

Example
^^^^^^^

.. code-block:: bash

    # Player options
    player=mpv --cache 2048
    player-no-close

    # Authenticate with Twitch
    twitch-oauth-token=mytoken


Plugin specific configuration file
----------------------------------

You may want to use specific options for some plugins only. This
can be accomplished by placing those settings inside a plugin specific
config file. Options inside these config files will override the main
config file when a URL matching the plugin is used.

Livecli expects this config to be named like the main config but
with ``.<plugin name>`` attached to the end.

Examples
^^^^^^^^

================= ====================================================
Platform          Location
================= ====================================================
Unix-like (POSIX) - $XDG_CONFIG_HOME/livecli/config\ **.twitch**
                  - ~/.liveclirc\ **.ustreamtv**
Windows           %APPDATA%\\livecli\\liveclirc\ **.youtube**
================= ====================================================

Have a look at the :ref:`list of plugins <plugin_matrix>` to see
the name of each built-in plugin.


Plugin specific usage
---------------------

Authenticating with Twitch
^^^^^^^^^^^^^^^^^^^^^^^^^^

It's possible to access subscription content on Twitch by giving Livecli
access to your account.

Authentication is done by creating an OAuth token that Livecli will
use to access your account. It's done like this:

.. sourcecode:: console

    $ livecli --twitch-oauth-authenticate


This will open a web browser where Twitch will ask you if you want to give
Livecli permission to access your account, then forwards you to a page
with further instructions on how to use it.


Authenticating with Crunchyroll
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Crunchyroll requires authenticating with a premium account to access some of
their content. To do so, the plugin provides a couple of options to input your
information, :option:`--crunchyroll-username` and :option:`--crunchyroll-password`.

You can login like this:

.. sourcecode:: console

    $ livecli --crunchyroll-username=xxxx --crunchyroll-password=xxx http://crunchyroll.com/a-crunchyroll-episode-link

.. note::

    If you omit the password, livecli will ask for it.

Once logged in, the plugin makes sure to save the session credentials to avoid
asking your username and password again.

Nevertheless, these credentials are valid for a limited amount of time, so it
might be a good idea to save your username and password in your
:ref:`configuration file <cli-liveclirc>` anyway.

.. warning::

    The API this plugin uses isn't supposed to be available to use it on
    computers. The plugin tries to blend in as a valid device using custom
    headers and following the API usual flow (e.g. reusing credentials), but
    this does not assure that your account will be safe from being spotted for
    unusual behavior.

HTTP proxy with Crunchyroll
^^^^^^^^^^^^^^^^^^^^^^^^^^^
You can use the :option:`--http-proxy` **and** :option:`--https-proxy`
options (you need both since the plugin uses both protocols) to access the
Crunchyroll servers through a proxy to be able to stream region locked content.

When doing this, it's very probable that you will get denied to access the
stream; this occurs because the session and credentials used by the plugin
where obtained when logged from your own region, and the server still assumes
you're in that region.

For this, the plugin provides the :option:`--crunchyroll-purge-credentials`
option, which removes your saved session and credentials and tries to log
in again using your username and password.

Sideloading plugins
-------------------

Livecli will attempt to load standalone plugins from these directories:

================= ====================================================
Platform          Location
================= ====================================================
Unix-like (POSIX) $XDG_CONFIG_HOME/livecli/plugins
Windows           %APPDATA%\\livecli\\plugins
================= ====================================================

.. note::

    If a plugin is added with the same name as a built-in plugin then
    the added plugin will take precedence. This is useful if you want
    to upgrade plugins independently of the Livecli version.


Playing built-in streaming protocols directly
---------------------------------------------

There are many types of streaming protocols used by services today and
Livecli supports most of them. It's possible to tell Livecli
to access a streaming protocol directly instead of relying on a plugin
to extract the streams from a URL for you.

A protocol can be accessed directly by specifying it in the URL format::

  protocol://path [key=value]

Accessing a stream that requires extra parameters to be passed along
(e.g. RTMP):

.. code-block:: console

    $ livecli "rtmp://streaming.server.net/playpath live=1 swfVfy=http://server.net/flashplayer.swf"

When passing parameters to the built-in stream plugins the values will either be treated as plain
strings, as is the case in the above example for ``swfVry``, or they will be interpreted as Python literals. For
example you can pass a Python dict or Python list as one of the parameters.

.. code-block:: console

    $ livecli "rtmp://streaming.server.net/playpath conn=['B:1', 'S:authMe', 'O:1', 'NN:code:1.23', 'NS:flag:ok', 'O:0']"
    $ livecli "hls://streaming.server.net/playpath params={'token': 'magicToken'}"

In the above examples ``conn`` will be passed as the Python list:

.. code-block:: python

    ['B:1', 'S:authMe', 'O:1', 'NN:code:1.23', 'NS:flag:ok', 'O:0']

and ``params`` will be passed as the Python dict:

.. code-block:: python

    {'token': 'magicToken'}

Most streaming technologies simply requires you to pass a HTTP URL, this is
a Adobe HDS stream:

.. code-block:: console

    $ livecli hds://streaming.server.net/playpath/manifest.f4m


Supported streaming protocols
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

============================== =================================================
Name                           Prefix
============================== =================================================
Adobe HTTP Dynamic Streaming   hds://
Akamai HD Adaptive Streaming   akamaihd://
Apple HTTP Live Streaming      hls:// [1]_
Real Time Messaging Protocol   rtmp:// rtmpe:// rtmps:// rtmpt:// rtmpte://
Progressive HTTP, HTTPS, etc   httpstream:// [1]_
============================== =================================================

.. [1] supports local files using the file:// protocol
.. _cli-options:

Proxy Support
-------------

You can use the :option:`--http-proxy` and :option:`--https-proxy` options to
change the proxy server that Livecli will use for HTTP and HTTPS requests respectively.
As HTTP and HTTPS requests can be handled by separate proxies, you may need to specify both
options if the plugin you use makes HTTP and HTTPS requests.

Both HTTP and SOCKS5 proxies are supported, authentication is supported for both types.

For example:

.. code-block:: console

    $ livecli --http-proxy "http://user:pass@10.10.1.10:3128/" --https-proxy "socks5://10.10.1.10:1242"


Command-line usage
------------------

.. code-block:: console

    $ livecli [OPTIONS] <URL> [STREAM]


.. argparse::
    :module: livecli_cli.argparser
    :attr: parser
