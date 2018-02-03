import re

from livecli.plugin import Plugin
from livecli.plugin.api import http, validate
from livecli.stream import HLSStream, HDSStream
from livecli.compat import urljoin
from livecli.stream import HTTPStream

__livecli_docs__ = {
    "domains": [
        "daserste.de",
    ],
    "geo_blocked": [
        "DE"
    ],
    "notes": "",
    "live": True,
    "vod": True,
    "last_update": "2017-05-03",
}


class ard_live(Plugin):
    swf_url = "http://live.daserste.de/lib/br-player/swf/main.swf"
    _url_re = re.compile(r"https?://(www.)?daserste.de/", re.I)
    _player_re = re.compile(r'''dataURL\s*:\s*(?P<q>['"])(?P<url>.*?)(?P=q)''')
    _player_url_schema = validate.Schema(
        validate.transform(_player_re.search),
        validate.any(
            None,
            validate.all(validate.get("url"), validate.text)
        )
    )
    _livestream_schema = validate.Schema(
        validate.xml_findall(".//assets"),
        validate.filter(lambda x: x.attrib.get("type") != "subtitles"),
        validate.get(0),
        validate.xml_findall(".//asset"),
        [validate.union({
            "url": validate.xml_findtext("./fileName"),
            "bitrate": validate.xml_findtext("./bitrateVideo")
        })])

    @classmethod
    def can_handle_url(cls, url):
        return cls._url_re.match(url) is not None

    def _get_streams(self):
        data_url = http.get(self.url, schema=self._player_url_schema)
        if data_url:
            res = http.get(urljoin(self.url, data_url))
            stream_info = http.xml(res, schema=self._livestream_schema)

            for stream in stream_info:
                url = stream["url"]
                try:
                    if ".m3u8" in url:
                        for s in HLSStream.parse_variant_playlist(self.session, url, name_key="bitrate").items():
                            yield s
                    elif ".f4m" in url:
                        for s in HDSStream.parse_manifest(self.session, url, pvswf=self.swf_url, is_akamai=True).items():
                            yield s
                    elif ".mp4" in url:
                        yield "{0}k".format(stream["bitrate"]), HTTPStream(self.session, url)
                except IOError as err:
                    self.logger.warning("Error parsing stream: {0}", err)


__plugin__ = ard_live
