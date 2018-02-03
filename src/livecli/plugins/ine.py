from __future__ import print_function

import json
import re

from livecli.plugin import Plugin
from livecli.plugin.api import http
from livecli.plugin.api import validate
from livecli.stream import HLSStream

__livecli_docs__ = {
    "domains": [
        "streaming.ine.com",
    ],
    "geo_blocked": [],
    "notes": "",
    "live": False,
    "vod": True,
    "last_update": "2017-02-06",
}


class INE(Plugin):
    url_re = re.compile(r"""https://streaming.ine.com/play\#?/
            ([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/?
            (.*?)""", re.VERBOSE)
    play_url = "https://streaming.ine.com/play/{vid}/watch"
    js_re = re.compile(r'''script type="text/javascript" src="(https://content.jwplatform.com/players/.*?)"''')
    jwplayer_re = re.compile(r'''jwConfig\s*=\s*(\{.*\});''', re.DOTALL)
    setup_schema = validate.Schema(
        validate.transform(jwplayer_re.search),
        validate.any(
            None,
            validate.all(
                validate.get(1),
                validate.transform(json.loads),
                {"playlist": [
                    {"sources": [{"file": validate.text,
                                  "type": validate.text}]}
                ]}
            )
        )
    )

    @classmethod
    def can_handle_url(cls, url):
        return cls.url_re.match(url) is not None

    def _get_streams(self):
        vid = self.url_re.match(self.url).group(1)
        self.logger.debug("Found video ID: {0}", vid)

        page = http.get(self.play_url.format(vid=vid))
        js_url_m = self.js_re.search(page.text)
        if js_url_m:
            js_url = js_url_m.group(1)
            self.logger.debug("Loading player JS: {0}", js_url)

            res = http.get(js_url)
            data = self.setup_schema.validate(res.text)
            for source in data["playlist"][0]["sources"]:
                if source["type"] == "hls":
                    return HLSStream.parse_variant_playlist(self.session, "https:" + source["file"])


__plugin__ = INE
