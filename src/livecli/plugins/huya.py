import re

from livecli.plugin import Plugin
from livecli.plugin.api import http, validate
from livecli.stream import HLSStream
from livecli.plugin.api import useragents
from livecli.utils import update_scheme

__livecli_docs__ = {
    "domains": [
        "huya.com",
    ],
    "geo_blocked": [],
    "notes": "",
    "live": True,
    "vod": False,
    "last_update": "2017-10-24",
}

HUYA_URL = "http://m.huya.com/%s"

_url_re = re.compile(r'http(s)?://(www\.)?huya.com/(?P<channel>[^/]+)', re.VERBOSE)
_hls_re = re.compile(r'^\s*<video\s+id="html5player-video"\s+src="(?P<url>[^"]+)"', re.MULTILINE)

_hls_schema = validate.Schema(
    validate.all(
        validate.transform(_hls_re.search),
        validate.any(
            None,
            validate.all(
                validate.get('url'),
                validate.transform(str)
            )
        )
    )
)


class Huya(Plugin):
    @classmethod
    def can_handle_url(self, url):
        return _url_re.match(url)

    def _get_streams(self):
        match = _url_re.match(self.url)
        channel = match.group("channel")

        http.headers.update({"User-Agent": useragents.IPAD})
        # Some problem with SSL on huya.com now, do not use https

        hls_url = http.get(HUYA_URL % channel, schema=_hls_schema)
        yield "live", HLSStream(self.session, update_scheme("http://", hls_url))


__plugin__ = Huya
