import re

from livecli.plugin import Plugin
from livecli.stream import HLSStream

__livecli_docs__ = {
    "domains": [
        "cdn.livestream.com",
        "original.livestream.com",
    ],
    "geo_blocked": [],
    "notes": "",
    "live": True,
    "vod": False,
    "last_update": "2017-04-25",
}

PLAYLIST_URL = "http://x{0}x.api.channel.livestream.com/3.0/playlist.m3u8"

_url_re = re.compile(r"http(s)?://(cdn|original)\.livestream\.com/(embed/)?(?P<channel>[^&?/]+)")


class OldLivestream(Plugin):
    @classmethod
    def can_handle_url(self, url):
        return _url_re.match(url)

    def _get_streams(self):
        match = _url_re.match(self.url)
        channel = match.group("channel")
        channel = channel.replace("_", "-")
        playlist_url = PLAYLIST_URL.format(channel)

        return HLSStream.parse_variant_playlist(self.session, playlist_url, check_streams=True)


__plugin__ = OldLivestream
