import re

from livecli.plugin import Plugin
from livecli.plugin.api import http
from livecli.stream import HLSStream

__livecli_docs__ = {
    "domains": [
        "tvcatchup.com",
    ],
    "geo_blocked": [
        "UK",
    ],
    "notes": "",
    "live": True,
    "vod": False,
    "last_update": "2017-11-01",
}

USER_AGENT = "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36"
_url_re = re.compile(r"http://(?:www\.)?tvcatchup.com/watch/\w+")
_stream_re = re.compile(r'''source.*?(?P<q>["'])(?P<stream_url>https?://.*m3u8\?.*clientKey=.*?)(?P=q)''')


class TVCatchup(Plugin):
    @classmethod
    def can_handle_url(cls, url):
        return _url_re.match(url)

    def _get_streams(self):
        """
        Finds the streams from tvcatchup.com.
        """
        http.headers.update({"User-Agent": USER_AGENT})
        res = http.get(self.url)

        match = _stream_re.search(res.text, re.IGNORECASE | re.MULTILINE)

        if match:
            stream_url = match.group("stream_url")

            if stream_url:
                if "_adp" in stream_url:
                    return HLSStream.parse_variant_playlist(self.session, stream_url)
                else:
                    return {'576p': HLSStream(self.session, stream_url)}


__plugin__ = TVCatchup
