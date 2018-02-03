# -*- coding: utf-8 -*-
import re

from livecli.compat import urlparse, parse_qsl
from livecli.plugin import Plugin
from livecli.plugin.api import http, validate
from livecli.stream import HLSStream

__livecli_docs__ = {
    "domains": [
        "rtbf.be",
    ],
    "geo_blocked": [
        "BE",
    ],
    "notes": "",
    "live": True,
    "vod": False,
    "last_update": "2018-01-19",
}


class RTBF(Plugin):
    """Livecli Plugin for RTBF"""

    _url_re = re.compile(r"""https?://(?:www\.)rtbf\.be/auvio/""")

    api_live_url = "https://www.rtbf.be/embed/d/ajax/refresh?id={0}"

    _live_schema = validate.Schema(
        {
            "data": validate.any(
                None,
                [],
                {
                    "streamUrlHls": validate.text,
                },
            ),
        },
        validate.get("data"),
    )

    @classmethod
    def can_handle_url(cls, url):
        return cls._url_re.match(url)

    def _get_live_stream(self, live_id):
        res = http.get(self.api_live_url.format(live_id))
        live_data = http.json(res, schema=self._live_schema)
        if not live_data:
            self.logger.debug("No data found.")
            return

        for s in HLSStream.parse_variant_playlist(self.session, live_data["streamUrlHls"]).items():
            yield s

    def _get_streams(self):
        params = dict(parse_qsl(urlparse(self.url).query))
        live_id = params.get("lid")

        if live_id:
            return self._get_live_stream(live_id)


__plugin__ = RTBF
