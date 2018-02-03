import re

from livecli.plugin import Plugin
from livecli.plugin.api import http, validate
from livecli.stream import RTMPStream, HLSStream

__livecli_docs__ = {
    "domains": [
        "rtvs.sk",
    ],
    "geo_blocked": [
        "SK",
    ],
    "notes": "",
    "live": True,
    "vod": False,
    "last_update": "2017-02-02",
}

RUURL = "b=chrome&p=win&v=56&f=0&d=1"

_url_re = re.compile(r"https?://www.rtvs.sk/televizia/live-[\w-]+")
_playlist_url_re = re.compile(r'"playlist": "([^"]+)"')

_playlist_schema = validate.Schema(
    [
        {
            "sources": [
                validate.any(
                    {
                        "type": "dash",
                        "file": validate.url(scheme="http")
                    }, {
                        "type": "hls",
                        "file": validate.url(scheme="http")
                    }, {
                        "type": "rtmp",
                        "file": validate.text,
                        "streamer": validate.url(scheme="rtmp")
                    }
                )
            ]
        }
    ],
    validate.get(0),
    validate.get("sources")
)


class Rtvs(Plugin):
    @classmethod
    def can_handle_url(cls, url):
        return _url_re.match(url)

    def _get_streams(self):
        res = http.get(self.url)
        match = _playlist_url_re.search(res.text)
        if match is None:
            return

        res = http.get(match.group(1) + RUURL)
        sources = http.json(res, schema=_playlist_schema)

        streams = {}

        for source in sources:
            if source["type"] == "rtmp":
                streams["rtmp_live"] = RTMPStream(self.session, {
                    "rtmp": source["streamer"],
                    "pageUrl": self.url,
                    "live": True
                })
            elif source["type"] == "hls":
                streams.update(HLSStream.parse_variant_playlist(self.session, source["file"]))

        return streams


__plugin__ = Rtvs
