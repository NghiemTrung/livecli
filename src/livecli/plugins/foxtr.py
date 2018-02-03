from __future__ import print_function
import re

from livecli.plugin import Plugin
from livecli.plugin.api import http
from livecli.stream import HLSStream

__livecli_docs__ = {
    "domains": [
        "fox.com.tr",
    ],
    "geo_blocked": [],
    "notes": "",
    "live": True,
    "vod": False,
    "last_update": "2017-02-12",
}


class FoxTR(Plugin):
    """
    Support for Turkish Fox live stream: http://www.fox.com.tr/canli-yayin
    """
    url_re = re.compile(r"https?://www.fox.com.tr/canli-yayin")
    playervars_re = re.compile(r"desktop\s*:\s*\[\s*\{\s*src\s*:\s*'(.*?)'", re.DOTALL)

    @classmethod
    def can_handle_url(cls, url):
        return cls.url_re.match(url) is not None

    def _get_streams(self):
        res = http.get(self.url)
        match = self.playervars_re.search(res.text)
        if match:
            stream_url = match.group(1)
            return HLSStream.parse_variant_playlist(self.session, stream_url)


__plugin__ = FoxTR
