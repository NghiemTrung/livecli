import re

from livecli.plugin import Plugin
from livecli.plugin.api import http
from livecli.plugins.theplatform import ThePlatform
from livecli.utils import update_scheme

__livecli_docs__ = {
    "domains": [
        "nbcsports.com",
    ],
    "geo_blocked": [
        "US",
    ],
    "notes": "Login not supported",
    "live": False,
    "vod": True,
    "last_update": "2017-04-04",
}


class NBCSports(Plugin):
    url_re = re.compile(r"https?://(?:www\.)?nbcsports\.com")
    embed_url_re = re.compile(r'''id\s*=\s*"vod-player"\s+src\s*=\s*"(?P<url>.*?)"''')

    @classmethod
    def can_handle_url(cls, url):
        return cls.url_re.match(url) is not None

    def _get_streams(self):
        res = http.get(self.url)
        m = self.embed_url_re.search(res.text)
        platform_url = m and m.group("url")

        if platform_url:
            url = update_scheme(self.url, platform_url)
            # hand off to ThePlatform plugin
            p = ThePlatform(url)
            p.bind(self.session, "plugin.nbcsports")
            return p.streams()


__plugin__ = NBCSports
