from __future__ import print_function

import re

from livecli.compat import urlparse, parse_qsl, urlunparse
from livecli.plugin import Plugin
from livecli.plugin.api import http
from livecli.stream import HLSStream

__livecli_docs__ = {
    "domains": [
        "srf.ch",
        "rsi.ch",
    ],
    "geo_blocked": [
        "CH",
    ],
    "notes": "",
    "live": True,
    "vod": False,
    "last_update": "2017-01-20",
}


class Swisstxt(Plugin):
    url_re = re.compile(r"""https?://(?:
        live\.(rsi)\.ch/|
        (?:www\.)?(srf)\.ch/sport/resultcenter
    )""", re.VERBOSE)
    api_url = "http://event.api.swisstxt.ch/v1/stream/{site}/byEventItemIdAndType/{id}/HLS"

    @classmethod
    def can_handle_url(cls, url):
        return cls.url_re.match(url) is not None and cls.get_event_id(url)

    @classmethod
    def get_event_id(cls, url):
        return dict(parse_qsl(urlparse(url).query.lower())).get("eventid")

    def get_stream_url(self, event_id):
        url_m = self.url_re.match(self.url)
        site = url_m.group(1) or url_m.group(2)
        api_url = self.api_url.format(id=event_id, site=site.upper())
        self.logger.debug("Calling API: {0}", api_url)

        stream_url = http.get(api_url).text.strip("\"'")

        parsed = urlparse(stream_url)
        query = dict(parse_qsl(parsed.query))
        return urlunparse(parsed._replace(query="")), query

    def _get_streams(self):
        stream_url, params = self.get_stream_url(self.get_event_id(self.url))
        return HLSStream.parse_variant_playlist(self.session,
                                                stream_url,
                                                params=params)


__plugin__ = Swisstxt
