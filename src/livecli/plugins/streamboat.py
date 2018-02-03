import re

from livecli.plugin import Plugin
from livecli.plugin.api import http
from livecli.stream import HLSStream

__livecli_docs__ = {
    "domains": [
        "streamboat.tv",
    ],
    "geo_blocked": [],
    "notes": "",
    "live": True,
    "vod": False,
    "last_update": "2016-09-19",
}

_RE_URL = re.compile(r'^https?://streamboat.tv/.+')
_RE_CDN = re.compile(r'"cdn_host"\s*:\s*"([^"]+)"')
_RE_PLAYLIST = re.compile(r'"playlist_url"\s*:\s*"([^"]+)"')


class StreamBoat(Plugin):

    @classmethod
    def can_handle_url(cls, url):
        return bool(_RE_URL.match(url))

    def _get_streams(self):
        res = http.get(self.url)
        text = res.text
        cdn = _RE_CDN.search(text).group(1)
        playlist_url = _RE_PLAYLIST.search(text).group(1)
        url = 'http://{}{}'.format(cdn, playlist_url)
        return dict(source=HLSStream(self.session, url))


__plugin__ = StreamBoat
