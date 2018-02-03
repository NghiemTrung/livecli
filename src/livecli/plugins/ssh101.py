import re

from livecli.plugin import Plugin
from livecli.plugin.api import http
from livecli.stream import HLSStream
from livecli.compat import urljoin

__livecli_docs__ = {
    "domains": [
        "ssh101.com",
    ],
    "geo_blocked": [],
    "notes": "",
    "live": True,
    "vod": False,
    "last_update": "",
    "broken": True,
}


class SSH101(Plugin):
    url_re = re.compile(r"https?://(?:\w+\.)?ssh101\.com/(.+)(/vod)?")
    src_re = re.compile(r'''source.*?src="(?P<url>.*?)"''')
    iframe_re = re.compile(r'''iframe.*?src="(?P<url>.*?)"''')

    @classmethod
    def can_handle_url(cls, url):
        return cls.url_re.match(url)

    def _get_streams(self):
        res = http.get(self.url)

        # some pages have embedded players
        iframe_m = self.iframe_re.search(res.text)
        if iframe_m:
            url = urljoin(self.url, iframe_m.group("url"))
            res = http.get(url)

        video = self.src_re.search(res.text)
        stream_src = video and video.group("url")

        if stream_src and stream_src.endswith("m3u8"):
            return HLSStream.parse_variant_playlist(self.session, stream_src)


__plugin__ = SSH101
