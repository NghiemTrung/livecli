from __future__ import print_function

import json
import re

from livecli.plugin import Plugin
from livecli.plugin.api import http
from livecli.plugin.api import validate
from livecli.stream import HLSStream
from livecli.compat import unquote

__livecli_docs__ = {
    "domains": [
        "showtv.com.tr",
        "haberturk.com",
        "showmax.com.tr",
        "showturk.com.tr",
        "bloomberght.com",
    ],
    "geo_blocked": [],
    "notes": "",
    "live": True,
    "vod": False,
    "last_update": "2016-12-15",
}


class CinerGroup(Plugin):
    """
    Support for the live stream on www.showtv.com.tr
    """
    url_re = re.compile(r"""https?://(?:www.)?
        (?:
            showtv.com.tr/canli-yayin(/showtv)?|
            haberturk.com/canliyayin|
            showmax.com.tr/canliyayin|
            showturk.com.tr/canli-yayin/showturk|
            bloomberght.com/tv|
            haberturk.tv/canliyayin
        )/?""", re.VERBOSE)
    stream_re = re.compile(r"""div .*? data-ht=(?P<quote>["'])(?P<data>.*?)(?P=quote)""", re.DOTALL)
    stream_data_schema = validate.Schema(
        validate.transform(stream_re.search),
        validate.any(
            None,
            validate.all(
                validate.get("data"),
                validate.transform(unquote),
                validate.transform(lambda x: x.replace("&quot;", '"')),
                validate.transform(json.loads),
                {
                    "ht_stream_m3u8": validate.url()
                },
                validate.get("ht_stream_m3u8")
            )
        )
    )

    @classmethod
    def can_handle_url(cls, url):
        return cls.url_re.match(url) is not None

    def _get_streams(self):
        res = http.get(self.url)
        stream_url = self.stream_data_schema.validate(res.text)
        if stream_url:
            return HLSStream.parse_variant_playlist(self.session, stream_url)


__plugin__ = CinerGroup
