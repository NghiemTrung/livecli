import re
import json

from livecli.plugin import Plugin
from livecli.plugin.api import http
from livecli.stream import HLSStream

__livecli_docs__ = {
    "domains": [
        "rtlxl.nl",
    ],
    "geo_blocked": [
        "NL",
    ],
    "notes": "",
    "live": False,
    "vod": True,
    "last_update": "2016-05-21",
}

_url_re = re.compile(r"""http(?:s)?://(?:\w+\.)?rtl.nl/video/(?P<uuid>.*?)\Z""", re.IGNORECASE)


class rtlxl(Plugin):
    @classmethod
    def can_handle_url(cls, url):
        return _url_re.match(url)

    def _get_streams(self):
        match = _url_re.match(self.url)
        uuid = match.group("uuid")
        videourlfeed = http.get('https://tm-videourlfeed.rtl.nl/api/url/{}?device=pc&drm&format=hls'.format(uuid)).text

        videourlfeedjson = json.loads(videourlfeed)
        playlist_url = videourlfeedjson["url"]

        return HLSStream.parse_variant_playlist(self.session, playlist_url)


__plugin__ = rtlxl
