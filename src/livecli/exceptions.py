class LivecliError(Exception):
    """Any error caused by Livecli will be caught
       with this exception."""


class PluginError(LivecliError):
    """Plugin related error."""


class NoStreamsError(LivecliError):
    def __init__(self, url):
        self.url = url
        err = "No streams found on this URL: {0}".format(url)
        Exception.__init__(self, err)


class NoPluginError(PluginError):
    """No relevant plugin has been loaded."""


class StreamError(LivecliError):
    """Stream related error."""


__all__ = ["LivecliError", "PluginError", "NoPluginError",
           "NoStreamsError", "StreamError"]
