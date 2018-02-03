from .session import Livecli


def streams(url, **params):
    """Attempts to find a plugin and extract streams from the *url*.

    *params* are passed to :func:`Plugin.streams`.

    Raises :exc:`NoPluginError` if no plugin is found.
    """

    session = Livecli()
    return session.streams(url, **params)
