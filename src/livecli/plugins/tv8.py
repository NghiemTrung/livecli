from __future__ import print_function
import re

from livecli.plugin import Plugin
from livecli.plugin.api import http
from livecli.plugin.api import validate
from livecli.stream import HLSStream

__livecli_docs__ = {
    "domains": [
        "tv8.com.tr",
    ],
    "geo_blocked": [],
    "notes": "",
    "live": True,
    "vod": False,
    "last_update": "2016-12-12",
}


class TV8(Plugin):
    """
    Support for the live stream on www.tv8.com.tr
    """
    url_re = re.compile(r"https?://www.tv8.com.tr/canli-yayin")

    player_config_re = re.compile(r"""
        configPlayer.source.media.push[ ]*\(
        [ ]*\{[ ]*'src':[ ]*"(.*?)",
        [ ]*type:[ ]*"application/x-mpegURL"[ ]*}[ ]*\);
    """, re.VERBOSE)
    player_config_schema = validate.Schema(
        validate.transform(player_config_re.search),
        validate.any(
            None,
            validate.all(
                validate.get(1),
                validate.url()
            )
        )
    )

    @classmethod
    def can_handle_url(cls, url):
        return cls.url_re.match(url) is not None

    def _get_streams(self):
        res = http.get(self.url)
        stream_url = self.player_config_schema.validate(res.text)
        if stream_url:
            return HLSStream.parse_variant_playlist(self.session, stream_url)


__plugin__ = TV8
