import re

from livecli.plugin import Plugin
from livecli.plugin.api import http
from livecli.plugin.api import useragents
from livecli.compat import urljoin
from livecli.stream import HLSStream

__livecli_docs__ = {
    "domains": [
        "brittv.co.uk",
    ],
    "geo_blocked": [],
    "notes": "",
    "live": True,
    "vod": False,
    "last_update": "2017-07-02",
}


class BritTV(Plugin):
    url_re = re.compile(r"https?://(?:www\.)?brittv\.co.uk/watch/")
    js_re = re.compile(r"""/js/brittv\.player\.js\.php\?key=([^'"]+)['"]""")
    player_re = re.compile(r"file: '(http://[^']+)'")

    @classmethod
    def can_handle_url(cls, url):
        return cls.url_re.match(url) is not None

    def _get_streams(self):
        res = http.get(self.url, headers={"User-Agent": useragents.CHROME})
        m = self.js_re.search(res.text)
        if m:
            self.logger.debug("Found js key: {0}", m.group(1))
            js_url = m.group(0)
            res = http.get(urljoin(self.url, js_url))

            for url in self.player_re.findall(res.text):
                if "adblock" not in url:
                    yield "live", HLSStream(self.session, url)


__plugin__ = BritTV
