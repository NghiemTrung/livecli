"""Plugin for NHK World, NHK Japan's english TV channel."""

import re

from livecli.plugin import Plugin
from livecli.plugin.api import http, validate
from livecli.stream import HLSStream

__livecli_docs__ = {
    "domains": [
        "nhk.or.jp",
    ],
    "geo_blocked": [],
    "notes": "",
    "live": True,
    "vod": False,
    "last_update": "2016-11-24",
}

API_URL = "http://{}.nhk.or.jp/nhkworld/app/tv/hlslive_web.xml"

_url_re = re.compile(r"http(?:s)?://(?:(\w+)\.)?nhk.or.jp/nhkworld")
_schema = validate.Schema(
    validate.xml_findtext("./main_url/wstrm")
)


class NHKWorld(Plugin):
    @classmethod
    def can_handle_url(cls, url):
        return _url_re.match(url) is not None

    def _get_streams(self):
        # get the HLS xml from the same sub domain as the main url, defaulting to www
        sdomain = _url_re.match(self.url).group(1) or "www"
        res = http.get(API_URL.format(sdomain))

        stream_url = http.xml(res, schema=_schema)
        return HLSStream.parse_variant_playlist(self.session, stream_url)


__plugin__ = NHKWorld
