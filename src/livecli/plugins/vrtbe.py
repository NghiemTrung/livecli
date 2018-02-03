import re

from livecli.plugin import Plugin
from livecli.plugin.api import http
from livecli.plugin.api import validate
from livecli.stream import HDSStream
from livecli.stream import HLSStream
from livecli.utils import parse_json

__livecli_docs__ = {
    "domains": [
        "vrt.be",
    ],
    "geo_blocked": [
        "BE",
    ],
    "notes": "",
    "live": True,
    "vod": True,
    "last_update": "2017-04-13",
}

_url_re = re.compile(r'''https?://www\.vrt\.be/vrtnu/(?:kanalen/(?P<channel>[^/]+)|\S+)''')
_json_re = re.compile(r'''(\173[^\173\175]+\175)''')

API_LIVE = 'https://services.vrt.be/videoplayer/r/live.json'
API_VOD = 'https://mediazone.vrt.be/api/v1/{0}/assets/{1}'

_stream_schema = validate.Schema({
    'targetUrls': [
        {
            'type': validate.text,
            'url': validate.text
        },
    ],
})


class VRTbe(Plugin):
    @classmethod
    def can_handle_url(cls, url):
        return _url_re.match(url)

    def _get_live_stream(self, channel):
        channel = 'vualto_{0}'.format(channel)
        _live_json_re = re.compile(r'''"{0}":\s(\173[^\173\175]+\175)'''.format(channel))

        res = http.get(API_LIVE)
        match = _live_json_re.search(res.text)
        if not match:
            return
        data = parse_json(match.group(1))

        hls_url = data['hls']

        if hls_url:
            for s in HLSStream.parse_variant_playlist(self.session, hls_url).items():
                yield s

    def _get_vod_stream(self):
        vod_url = self.url
        if vod_url.endswith('/'):
            vod_url = vod_url[:-1]

        json_url = '{0}.securevideo.json'.format(vod_url)

        res = http.get(json_url)
        match = _json_re.search(res.text)
        if not match:
            return
        data = parse_json(match.group(1))

        res = http.get(API_VOD.format(data['clientid'], data['mzid']))
        data = http.json(res, schema=_stream_schema)

        for d in data['targetUrls']:
            if d['type'] == 'HDS':
                hds_url = d['url']
                for s in HDSStream.parse_manifest(self.session, hds_url).items():
                    yield s

            if d['type'] == 'HLS':
                hls_url = d['url']
                for s in HLSStream.parse_variant_playlist(self.session, hls_url).items():
                    yield s

    def _get_streams(self):
        match = _url_re.match(self.url)

        channel = match.group('channel')

        if channel:
            return self._get_live_stream(channel)
        else:
            return self._get_vod_stream()


__plugin__ = VRTbe
