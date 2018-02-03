import re

from livecli.plugin import Plugin
from livecli.plugin.api import http
from livecli.plugin.api import validate
from livecli.stream import HLSStream

__livecli_docs__ = {
    "domains": [
        "garena.live",
    ],
    "geo_blocked": [],
    "notes": "",
    "live": True,
    "vod": False,
    "last_update": "2017-03-19",
}

_url_re = re.compile(r"https?\:\/\/garena\.live\/(?:(?P<channel_id>\d+)|(?P<alias>\w+))")


class Garena(Plugin):
    API_INFO = "https://garena.live/api/channel_info_get"
    API_STREAM = "https://garena.live/api/channel_stream_get"

    _info_schema = validate.Schema(
        {
            "reply": validate.any({
                "channel_id": int,
            }, None),
            "result": validate.text
        }
    )
    _stream_schema = validate.Schema(
        {
            "reply": validate.any({
                "streams": [
                    {
                        "url": validate.text,
                        "resolution": int,
                        "bitrate": int,
                        "format": int
                    }
                ]
            }, None),
            "result": validate.text
        }
    )

    @classmethod
    def can_handle_url(self, url):
        return _url_re.match(url)

    def _post_api(self, api, payload, schema):
        res = http.post(api, json=payload)
        data = http.json(res, schema=schema)

        if data["result"] == "success":
            post_data = data["reply"]
            return post_data

    def _get_streams(self):
        match = _url_re.match(self.url)
        if match.group("alias"):
            payload = {"alias": match.group("alias")}
            info_data = self._post_api(self.API_INFO, payload, self._info_schema)
            channel_id = info_data["channel_id"]
        elif match.group("channel_id"):
            channel_id = int(match.group("channel_id"))

        if channel_id:
            payload = {"channel_id": channel_id}
            stream_data = self._post_api(self.API_STREAM, payload, self._stream_schema)
            for stream in stream_data["streams"]:
                n = "{0}p".format(stream["resolution"])
                if stream["format"] == 3:
                    s = HLSStream(self.session, stream["url"])
                    yield n, s


__plugin__ = Garena
