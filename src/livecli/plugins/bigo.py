import re

from livecli.cache import Cache
from livecli.plugin import Plugin
from livecli.plugin.api import http
from livecli.plugin.api import useragents
from livecli.stream import HLSStream

__livecli_docs__ = {
    "domains": [
        "bigo.tv",
    ],
    "geo_blocked": [],
    "notes": "",
    "live": True,
    "vod": False,
    "last_update": "2018-01-21",
}


class Bigo(Plugin):
    _url_re = re.compile(r"https?://(www\.)?bigo\.tv/[\w\d]+")
    _video_re = re.compile(r"""videoSrc:\s?["'](?P<url>[^"']+)["']""")

    @classmethod
    def can_handle_url(cls, url):
        return cls._url_re.match(url) is not None

    def _check_options(self):
        if not self.session.get_option("hls-segment-ignore-number"):
            self.session.set_option("hls-segment-ignore-number", 20)
        if not self.session.get_option("hls-session-reload"):
            self.session.set_option("hls-session-reload", 30)

    def _update_cache(self, hls_url):
        cache = Cache(
            filename="streamdata.json",
            key_prefix="cache:{0}".format(hls_url)
        )
        cache.set("cache_stream_name", "live", (self.session.get_option("hls-session-reload") + 60))
        cache.set("cache_url", self.url, (self.session.get_option("hls-session-reload") + 60))

    def _get_streams(self):
        res = http.get(self.url,
                       allow_redirects=True,
                       headers={"User-Agent": useragents.IPHONE_6})
        m = self._video_re.search(res.text)
        if not m:
            return

        self._check_options()
        videourl = m.group("url")
        self._update_cache(videourl)
        yield "live", HLSStream(self.session, videourl)


__plugin__ = Bigo
