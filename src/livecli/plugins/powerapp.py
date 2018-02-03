from __future__ import print_function
import re

from livecli.plugin import Plugin
from livecli.plugin.api import http
from livecli.plugin.api import validate
from livecli.stream import HLSStream

__livecli_docs__ = {
    "domains": [
        "powerapp.com.tr",
    ],
    "geo_blocked": [],
    "notes": "",
    "live": True,
    "vod": False,
    "last_update": "2016-12-16",
}


class PowerApp(Plugin):
    url_re = re.compile(r"https?://(?:www.)?powerapp.com.tr/tv/(\w+)")
    api_url = "http://api.powergroup.com.tr/Channels/{0}/?appRef=iPowerWeb&apiVersion=11"
    api_schema = validate.Schema(validate.all({
        "errorCode": 0,
        "response": {
            "channel_stream_url": validate.url()
        }
    }, validate.get("response")))

    @classmethod
    def can_handle_url(cls, url):
        return cls.url_re.match(url) is not None

    def _get_streams(self):
        channel = self.url_re.match(self.url).group(1)

        res = http.get(self.api_url.format(channel))
        data = http.json(res, schema=self.api_schema)

        return HLSStream.parse_variant_playlist(self.session, data["channel_stream_url"])


__plugin__ = PowerApp
