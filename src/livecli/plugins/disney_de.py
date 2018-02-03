"""Plugin for Disney (Channel) Germany

Supports:
    - http://video.disney.de/sehen/*
    - http://disneychannel.de/sehen/*
    - http://disneychannel.de/livestream
"""

import re

from livecli.plugin import Plugin
from livecli.plugin.api import http
from livecli.plugin.api.utils import parse_json
from livecli.stream import HLSStream

__livecli_docs__ = {
    "domains": [
        "disneychannel.de",
        "disney.de"
    ],
    "geo_blocked": [
        "DE",
    ],
    "notes": "",
    "live": True,
    "vod": True,
    "last_update": "2015-01-25",
}

_url_re = re.compile(r"http(s)?://(\w+\.)?disney(channel)?.de/")

# stream urls are in `Grill.burger`->stack->data->externals->data
_stream_hls_re = re.compile(r"\"hlsStreamUrl\":\s*(\"[^\"]+\")")
_stream_data_re = re.compile(r"\"dataUrl\":\s*(\"[^\"]+\")")


class DisneyDE(Plugin):
    @classmethod
    def can_handle_url(cls, url):
        return _url_re.match(url)

    def _get_streams(self):
        res = http.get(self.url)
        match = (_stream_hls_re.search(res.text) or
                 _stream_data_re.search(res.text))
        if not match:
            return

        stream_url = parse_json(match.group(1))

        return HLSStream.parse_variant_playlist(self.session, stream_url)


__plugin__ = DisneyDE
