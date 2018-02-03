'''
Plugin for vidio.com
- https://www.vidio.com/live/5075-dw-tv-stream
- https://www.vidio.com/watch/766861-5-rekor-fantastis-zidane-bersama-real-madrid
'''
import re

from livecli.plugin import Plugin
from livecli.plugin.api import http
from livecli.stream import HLSStream

__livecli_docs__ = {
    "domains": [
        "vidio.com",
    ],
    "geo_blocked": [],
    "notes": "",
    "live": True,
    "vod": True,
    "last_update": "2017-07-05",
}

_url_re = re.compile(r"https?://(?:www\.)?vidio\.com/(?:en/)?(?P<type>live|watch)/(?P<id>\d+)-(?P<name>[^/?#&]+)")
_playlist_re = re.compile(r'''hls-url=["'](?P<url>[^"']+)["']''')


class Vidio(Plugin):
    @classmethod
    def can_handle_url(cls, url):
        return _url_re.match(url)

    def _get_streams(self):
        res = http.get(self.url)

        match = _playlist_re.search(res.text)
        if match is None:
            return

        url = match.group('url')

        if url:
            self.logger.debug('HLS URL: {0}'.format(url))
            for s in HLSStream.parse_variant_playlist(self.session, url).items():
                yield s


__plugin__ = Vidio
