import re

from livecli.plugin import Plugin
from livecli.plugin.api import http
from livecli.stream import HDSStream

__livecli_docs__ = {
    "domains": [
        "antenna.gr",
    ],
    "geo_blocked": [],
    "notes": "",
    "live": False,
    "vod": True,
    "last_update": "2015-11-24",
}

_url_re = re.compile(r"(http(s)?://(\w+\.)?antenna.gr)/webtv/watch\?cid=.+")
_playlist_re = re.compile(r"playlist:\s*\"(/templates/data/jplayer\?cid=[^\"]+)")
_manifest_re = re.compile(r"jwplayer:source\s+file=\"([^\"]+)\"")
_swf_re = re.compile(r"<jwplayer:provider>(http[^<]+)</jwplayer:provider>")


class Antenna(Plugin):
    @classmethod
    def can_handle_url(self, url):
        return _url_re.match(url)

    def _get_streams(self):

        # Discover root
        match = _url_re.search(self.url)
        root = match.group(1)

        # Download main URL
        res = http.get(self.url)

        # Find playlist
        match = _playlist_re.search(res.text)
        playlist_url = root + match.group(1) + "d"

        # Download playlist
        res = http.get(playlist_url)

        # Find manifest
        match = _manifest_re.search(res.text)
        manifest_url = match.group(1)

        # Find SWF
        match = _swf_re.search(res.text)
        swf_url = match.group(1)

        streams = {}
        streams.update(
            HDSStream.parse_manifest(self.session, manifest_url, pvswf=swf_url)
        )

        return streams


__plugin__ = Antenna
