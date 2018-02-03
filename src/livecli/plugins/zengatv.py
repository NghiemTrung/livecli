import re

from livecli.plugin import Plugin
from livecli.plugin.api import http
from livecli.plugin.api import useragents
from livecli.stream import HLSStream

__livecli_docs__ = {
    "domains": [
        "zengatv.com",
    ],
    "geo_blocked": [],
    "notes": "",
    "live": True,
    "vod": False,
    "last_update": "2018-01-11",
}


class ZengaTV(Plugin):
    """Livecli Plugin for livestreams on zengatv.com"""

    _url_re = re.compile(r"https?://(www\.)?zengatv\.com/\w+")
    _id_re = re.compile(r"""id=(?P<q>["'])dvrid(?P=q)\svalue=(?P=q)(?P<id>[^"']+)(?P=q)""")
    _id_2_re = re.compile(r"""LivePlayer\(.+["'](?P<id>D\d+)["']""")

    api_url = "http://www.zengatv.com/changeResulation/"

    @classmethod
    def can_handle_url(cls, url):
        return cls._url_re.match(url) is not None

    def _get_streams(self):
        headers = {
            "User-Agent": useragents.FIREFOX,
            "Referer": self.url,
        }

        res = http.get(self.url, headers=headers)
        for id_re in (self._id_re, self._id_2_re):
            m = id_re.search(res.text)
            if not m:
                continue
            break

        if not m:
            self.logger.error("No video id found")
            return

        dvr_id = m.group("id")
        self.logger.debug("Found video id: {0}".format(dvr_id))
        data = {"feed": "hd", "dvrId": dvr_id}
        res = http.post(self.api_url, headers=headers, data=data)
        if res.status_code == 200:
            for s in HLSStream.parse_variant_playlist(self.session, res.text, headers=headers).items():
                yield s


__plugin__ = ZengaTV
