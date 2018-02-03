import re

from time import time

from livecli.plugin import Plugin, PluginError
from livecli.plugin.api import http, validate
from livecli.stream import RTMPStream, HLSStream

__livecli_docs__ = {
    "domains": [
        "streamingvideoprovider.co.uk",
    ],
    "geo_blocked": [],
    "notes": "rtmpdump K-S-V",
    "live": True,
    "vod": False,
    "last_update": "2014-07-13",
}

SWF_URL = "http://play.streamingvideoprovider.com/player2.swf"
API_URL = "http://player.webvideocore.net/index.php"

_url_re = re.compile(
    r"http(s)?://(\w+\.)?streamingvideoprovider.co.uk/(?P<channel>[^/&?]+)"
)
_hls_re = re.compile(r"'(http://.+\.m3u8)'")

_rtmp_schema = validate.Schema(
    validate.xml_findtext("./info/url"),
    validate.url(scheme="rtmp")
)
_hls_schema = validate.Schema(
    validate.transform(_hls_re.search),
    validate.any(
        None,
        validate.all(
            validate.get(1),
            validate.url(
                scheme="http",
                path=validate.endswith("m3u8")
            )
        )
    )
)


class Streamingvideoprovider(Plugin):
    @classmethod
    def can_handle_url(self, url):
        return _url_re.match(url)

    def _get_hls_stream(self, channel_name):
        params = {
            "l": "info",
            "a": "ajax_video_info",
            "file": channel_name,
            "rid": time()
        }
        playlist_url = http.get(API_URL, params=params, schema=_hls_schema)
        if not playlist_url:
            return

        return HLSStream(self.session, playlist_url)

    def _get_rtmp_stream(self, channel_name):
        params = {
            "l": "info",
            "a": "xmlClipPath",
            "clip_id": channel_name,
            "rid": time()
        }
        res = http.get(API_URL, params=params)
        rtmp_url = http.xml(res, schema=_rtmp_schema)

        return RTMPStream(self.session, {
            "rtmp": rtmp_url,
            "swfVfy": SWF_URL,
            "live": True
        })

    def _get_streams(self):
        match = _url_re.match(self.url)
        channel_name = match.group("channel")

        try:
            stream = self._get_rtmp_stream(channel_name)
            yield "live", stream
        except PluginError as err:
            self.logger.error("Unable to extract RTMP stream: {0}", err)

        try:
            stream = self._get_hls_stream(channel_name)
            if stream:
                yield "live", stream
        except PluginError as err:
            self.logger.error("Unable to extract HLS stream: {0}", err)


__plugin__ = Streamingvideoprovider
