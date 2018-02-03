import re

from livecli.plugin import Plugin
from livecli.stream import HLSStream

_playlist_url = "https://www.facebook.com/video/playback/playlist.m3u8?v={0}"

_url_re = re.compile(r"http(s)?://(www\.)?facebook\.com/[^/]+/videos/(?P<video_id>\d+)")

__livecli_docs__ = {
    "domains": [
        "facebook.com",
    ],
    "geo_blocked": [],
    "notes": "",
    "live": True,
    "vod": False,
    "last_update": "2016-11-30",
    "broken": True,
}


class Facebook(Plugin):
    @classmethod
    def can_handle_url(cls, url):
        return _url_re.match(url)

    def _get_streams(self):
        match = _url_re.match(self.url)
        video = match.group("video_id")

        playlist = _playlist_url.format(video)

        return HLSStream.parse_variant_playlist(self.session, playlist)


__plugin__ = Facebook
