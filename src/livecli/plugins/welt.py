# -*- coding: utf-8 -*-
import re

from livecli.compat import quote
from livecli.plugin import Plugin
from livecli.plugin.api import http
from livecli.plugin.api import useragents
from livecli.stream import HLSStream
from livecli.stream import HTTPStream

__livecli_docs__ = {
    "domains": [
        "welt.de",
    ],
    "geo_blocked": [
        "DE",
    ],
    "notes": "",
    "live": True,
    "vod": True,
    "last_update": "2018-01-18",
}


class Welt(Plugin):
    """Livecli Plugin for welt.de"""

    _files_re = re.compile(r"""["']file["']:\s?["'](?P<url>[^"']+\.(?:m3u8|mp4)(?:[^"']+)?)["']""")
    _mp4_bitrate_re = re.compile(r"""_(?P<bitrate>\d+)\.mp4""")
    _url_re = re.compile(r"""https?://(?:www\.)?welt\.de/""")

    @classmethod
    def can_handle_url(cls, url):
        return cls._url_re.match(url)

    def _get_streams(self):
        headers = {
            "User-Agent": useragents.FIREFOX,
            "Referer": self.url
        }
        res = http.get(self.url, headers=headers)
        files = self._files_re.findall(res.text)
        if files is None:
            return

        files = list(set(files))
        for url in files:
            if ".m3u8" in url:
                if url.startswith("https://weltmediathek-vh."):
                    url = "https://www.welt.de/video/services/token/{0}".format(quote(url, safe=""))
                    res = http.get(url, headers=headers)
                    r_json = http.json(res)
                    url = r_json["urlWithToken"]
                for s in HLSStream.parse_variant_playlist(self.session, url, headers=headers).items():
                    yield s
            elif url.endswith(".mp4"):
                m = self._mp4_bitrate_re.search(url)
                bitrate = m.group("bitrate")
                if bitrate:
                    name = "{0}k".format(bitrate)
                else:
                    name = "mp4"
                yield name, HTTPStream(self.session, url, headers=headers)


__plugin__ = Welt
