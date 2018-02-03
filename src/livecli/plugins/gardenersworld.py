from __future__ import print_function

import re

from livecli.plugin import Plugin
from livecli.plugin.api import http
from livecli.plugins.brightcove import BrightcovePlayer

__livecli_docs__ = {
    "domains": [
        "gardenersworld.com",
    ],
    "geo_blocked": [],
    "notes": "",
    "live": False,
    "vod": True,
    "last_update": "2017-04-07",
}


class GardenersWorld(Plugin):
    url_re = re.compile(r"https?://(?:www\.)?gardenersworld\.com/")
    object_re = re.compile('''<object.*?id="brightcove-pod-object".*?>(.*?)</object>''', re.DOTALL)
    param_re = re.compile('''<param.*?name="(.*?)".*?value="(.*?)".*?/>''')

    @classmethod
    def can_handle_url(cls, url):
        return cls.url_re.match(url) is not None

    def _get_streams(self):
        page = http.get(self.url)
        object_m = self.object_re.search(page.text)
        if object_m:
            object_t = object_m.group(1)
            params = {}
            for param_m in self.param_re.finditer(object_t):
                params[param_m.group(1)] = param_m.group(2)

            return BrightcovePlayer.from_player_key(self.session,
                                                    params.get("playerID"),
                                                    params.get("playerKey"),
                                                    params.get("videoID"),
                                                    url=self.url)


__plugin__ = GardenersWorld
