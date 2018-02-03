import re

from livecli.plugin import Plugin
from livecli.plugin.api import http
from livecli.plugin.api import validate
from livecli.stream import HLSStream, HTTPStream

__livecli_docs__ = {
    "domains": [
        "euronews.com",
    ],
    "geo_blocked": [],
    "notes": "",
    "live": True,
    "vod": False,
    "last_update": "2017-05-10",
}


class Euronews(Plugin):
    _url_re = re.compile(r"http(?:s)?://(\w+)\.?euronews.com/(live|.*)")
    _re_vod = re.compile(r'<meta\s+property="og:video"\s+content="(http.*?)"\s*/>')
    _live_api_url = "http://{0}.euronews.com/api/watchlive.json"
    _live_schema = validate.Schema({
        u"url": validate.url()
    })
    _stream_api_schema = validate.Schema({
        u'status': u'ok',
        u'primary': validate.url(),
        validate.optional(u'backup'): validate.url()
    })

    @classmethod
    def can_handle_url(cls, url):
        return cls._url_re.match(url)

    def _get_vod_stream(self):
        """
        Find the VOD video url
        :return: video url
        """
        res = http.get(self.url)
        video_urls = self._re_vod.findall(res.text)
        if len(video_urls):
            return dict(vod=HTTPStream(self.session, video_urls[0]))

    def _get_live_streams(self, subdomain):
        """
        Get the live stream in a particular language
        :param subdomain:
        :return:
        """
        res = http.get(self._live_api_url.format(subdomain))
        live_res = http.json(res, schema=self._live_schema)
        api_res = http.get(live_res[u"url"])
        stream_data = http.json(api_res, schema=self._stream_api_schema)
        return HLSStream.parse_variant_playlist(self.session, stream_data[u'primary'])

    def _get_streams(self):
        """
        Find the streams for euronews
        :return:
        """
        match = self._url_re.match(self.url)
        subdomain, path = match.groups()

        if path == "live":
            return self._get_live_streams(subdomain)
        else:
            return self._get_vod_stream()


__plugin__ = Euronews
