"""Plugin for younow.com by WeinerRinkler"""

import re

from livecli.plugin import Plugin
from livecli.plugin.api import http
from livecli.stream import RTMPStream

__livecli_docs__ = {
    "domains": [
        "younow.com",
    ],
    "geo_blocked": [],
    "notes": "",
    "live": True,
    "vod": False,
    "last_update": "2015-07-21",
}

jsonapi = "https://api.younow.com/php/api/broadcast/info/curId=0/user="

# http://younow.com/channel/
_url_re = re.compile(r"http(s)?://(\w+.)?younow.com/(?P<channel>[^/&?]+)")


def getStreamURL(channel):
    url = jsonapi + channel
    res = http.get(url)
    streamerinfo = http.json(res)
    # print(streamerinfo)

    if not any("media" in s for s in streamerinfo):
        print("User offline or invalid")
        return
    else:
        streamdata = streamerinfo['media']
        # print(streamdata)
        streamurl = "rtmp://" + streamdata['host'] + streamdata['app'] + "/" + streamdata['stream']
        # print (streamurl)

    return streamurl


class younow(Plugin):
    @classmethod
    def can_handle_url(self, url):
        return _url_re.match(url)

    def _get_streams(self):
        match = _url_re.match(self.url)
        channel = match.group("channel")

        streamurl = getStreamURL(channel)
        if not streamurl:
            return
        streams = {}
        streams["live"] = RTMPStream(self.session, {
            "rtmp": streamurl,
            "live": True
        })

        return streams


__plugin__ = younow
