import random
import re
import time

from livecli.plugin import Plugin
from livecli.plugin.api import http
from livecli.plugin.api import useragents
from livecli.plugin.api import validate
from livecli.stream import HLSStream

__livecli_docs__ = {
    "domains": [
        "1tv.ru",
        "chetv.ru",
        "ctc.ru",
        "ctclove.ru",
        "domashny.ru",
    ],
    "geo_blocked": [
        "RU",
    ],
    "notes": "",
    "live": True,
    "vod": False,
    "last_update": "2018-01-18",
}


class PerviyKanal(Plugin):
    """Livecli Plugin for Livestreams of
        - 1tv.ru
        - chetv.ru
        - ctc.ru
        - ctclove.ru
        - domashny.ru
    """

    API_HLS_SESSION = "https://stream.1tv.ru/get_hls_session"

    channel_map = {
        "1tv": "1tv",
        "chetv": "ctc-che",
        "ctc": "ctc",
        "ctclove": "ctc-love",
        "domashny": "ctc-dom",
    }

    _session_schema = validate.Schema(
        {
            "s": validate.text
        }
    )

    _url_re = re.compile(r"""https?://
        (?:(?:media|stream|www)?\.)?
        (?P<domain>
            1tv
            |
            chetv
            |
            ctc(?:love)?
            |
            domashny
            )\.ru/
                (?:
                embed/ctcmedia/(?P<channel>[^/?]+.).html
                |
                embedlive
                |
                iframed
                |
                live
                |
                online
                )
        """, re.VERBOSE)

    @classmethod
    def can_handle_url(cls, url):
        return cls._url_re.match(url)

    def _get_streams(self):
        match = self._url_re.match(self.url)
        channel = match.group("channel")
        if not channel:
            channel = match.group("domain")
            channel = self.channel_map[channel]

        headers = {
            "Referer": self.url,
            "User-Agent": useragents.FIREFOX
        }

        cdn = random.choice(["cdn8", "edge1", "edge3"])
        query_e = "e={0}".format(int(time.time()))
        server = random.choice(["9", "10"])
        subdomain = "mobdrm"
        hls_url = "https://{subdomain}.1tv.ru/hls-live{server}/streams/{channel}/{channel}.m3u8?cdn=https://{cdn}.1internet.tv&{query}".format(
            cdn=cdn,
            channel=channel,
            query=query_e,
            server=server,
            subdomain=subdomain
        )

        res = http.get(self.API_HLS_SESSION, headers=headers)
        json_session = http.json(res, schema=self._session_schema)
        hls_url = "{url}&s={session}".format(url=hls_url, session=json_session["s"])

        if hls_url:
            self.logger.debug("HLS URL: {0}".format(hls_url))
            streams = HLSStream.parse_variant_playlist(self.session, hls_url, headers=headers, name_fmt="{pixels}_{bitrate}")
            if not streams:
                return {"live": HLSStream(self.session, hls_url, headers=headers)}
            else:
                return streams


__plugin__ = PerviyKanal
