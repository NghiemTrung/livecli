import re

from livecli.plugin import Plugin
from livecli.plugin.api import http
from livecli.plugins.theplatform import ThePlatform
from livecli.utils import update_scheme

__livecli_docs__ = {
    "domains": [
        "nbc.com",
    ],
    "geo_blocked": [
        "US",
    ],
    "notes": "Login not supported",
    "live": False,
    "vod": True,
    "last_update": "2017-04-07",
}


class NBC(Plugin):
    url_re = re.compile(r"https?://(?:www\.)?nbc\.com")
    embed_url_re = re.compile(r'''(?P<q>["'])embedURL(?P=q)\s*:\s*(?P<q2>["'])(?P<url>.*?)(?P=q2)''')

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
            p.bind(self.session, "plugin.nbc")
            return p.streams()


__plugin__ = NBC
