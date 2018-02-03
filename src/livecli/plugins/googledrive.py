import re

from livecli.compat import parse_qsl
from livecli.plugin import Plugin
from livecli.plugin.api import http
from livecli.stream import HTTPStream

__livecli_docs__ = {
    "domains": [
        "docs.google.com",
        "drive.google.com",
    ],
    "geo_blocked": [],
    "notes": "",
    "live": False,
    "vod": True,
    "last_update": "2017-05-21",
}


class GoogleDocs(Plugin):
    url_re = re.compile(r"https?://(?:drive|docs).google.com/file/d/([^/]+)/?")
    api_url = "https://docs.google.com/get_video_info"

    @classmethod
    def can_handle_url(cls, url):
        return cls.url_re.match(url) is not None

    def _get_streams(self):
        docid = self.url_re.match(self.url).group(1)
        self.logger.debug("Google Docs ID: {0}", docid)
        res = http.get(self.api_url, params=dict(docid=docid))
        data = dict(parse_qsl(res.text))

        if data["status"] == "ok":
            fmts = dict([s.split('/')[:2] for s in data["fmt_list"].split(",")])
            streams = [s.split('|') for s in data["fmt_stream_map"].split(",")]
            for qcode, url in streams:
                _, h = fmts[qcode].split("x")
                yield "{0}p".format(h), HTTPStream(self.session, url)
        else:
            self.logger.error("{0} (ID: {1})", data["reason"], docid)


__plugin__ = GoogleDocs
