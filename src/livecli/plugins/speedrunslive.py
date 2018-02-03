import re

from livecli.plugin import Plugin

__livecli_docs__ = {
    "domains": [
        "speedrunslive.com",
    ],
    "geo_blocked": [],
    "notes": "",
    "live": True,
    "vod": False,
    "last_update": "2014-06-06",
}

TWITCH_URL_FORMAT = "http://www.twitch.tv/{0}"

_url_re = re.compile(r"http://(?:www\.)?speedrunslive.com/#!/(?P<user>\w+)")


class SpeedRunsLive(Plugin):
    @classmethod
    def can_handle_url(self, url):
        return _url_re.match(url)

    def _get_streams(self):
        match = _url_re.match(self.url)
        username = match.group("user")
        url = TWITCH_URL_FORMAT.format(username)
        return self.session.streams(url)


__plugin__ = SpeedRunsLive
