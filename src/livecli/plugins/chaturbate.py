import re
import uuid

from livecli.plugin import Plugin
from livecli.plugin.api import http
from livecli.plugin.api import validate
from livecli.stream import HLSStream

__livecli_docs__ = {
    "domains": [
        "chaturbate.com",
    ],
    "geo_blocked": [],
    "notes": "",
    "live": True,
    "vod": False,
    "last_update": "2017-04-05",
}

API_HLS = "https://chaturbate.com/get_edge_hls_url_ajax/"

_url_re = re.compile(r"https?://(\w+\.)?chaturbate\.com/(?P<username>\w+)")

_post_schema = validate.Schema(
    {
        "url": validate.text,
        "room_status": validate.text,
        "success": int
    }
)


class Chaturbate(Plugin):
    @classmethod
    def can_handle_url(cls, url):
        return _url_re.match(url)

    def _get_streams(self):
        match = _url_re.match(self.url)
        username = match.group("username")

        CSRFToken = str(uuid.uuid4().hex.upper()[0:32])

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "X-CSRFToken": CSRFToken,
            "X-Requested-With": "XMLHttpRequest",
            "Referer": self.url,
        }

        cookies = {
            "csrftoken": CSRFToken,
        }

        post_data = "room_slug={0}&bandwidth=high".format(username)

        res = http.post(API_HLS, headers=headers, cookies=cookies, data=post_data)
        data = http.json(res, schema=_post_schema)

        if data["success"] is True and data["room_status"] == "public":
            for s in HLSStream.parse_variant_playlist(self.session, data["url"]).items():
                yield s


__plugin__ = Chaturbate
