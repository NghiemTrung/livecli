import re

from livecli.plugin import Plugin
from livecli.plugin.api import http
from livecli.plugin.api import validate
from livecli.stream import HTTPStream
from livecli.utils import parse_json

__livecli_docs__ = {
    "domains": [
        "radio.net",
        "radio.at",
        "radio.de",
        "radio.dk",
        "radio.es",
        "radio.fr",
        "radio.it",
        "radio.pl",
        "radio.pt",
        "radio.se",
    ],
    "geo_blocked": [],
    "notes": "",
    "live": True,
    "vod": False,
    "last_update": "2017-06-04",
}


class RadioNet(Plugin):
    _url_re = re.compile(r"https?://(\w+)\.radio\.(net|at|de|dk|es|fr|it|pl|pt|se)")
    _stream_data_re = re.compile(r'\bstation\s*:\s*(\{.+\}),?\s*')

    _stream_schema = validate.Schema(
        validate.transform(_stream_data_re.search),
        validate.any(
            None,
            validate.all(
                validate.get(1),
                validate.transform(parse_json),
                {
                    'stationType': validate.text,
                    'streamUrls': validate.all([{
                        'bitRate': int,
                        'streamUrl': validate.url()
                    }])
                },
            )
        )
    )

    @classmethod
    def can_handle_url(cls, url):
        return cls._url_re.match(url)

    def _get_streams(self):
        streams = http.get(self.url, schema=self._stream_schema)
        if streams is None:
            return

        # Ignore non-radio streams (podcasts...)
        if streams['stationType'] != 'radio_station':
            return

        stream_urls = []
        for stream in streams['streamUrls']:
            if stream['streamUrl'] in stream_urls:
                continue

            if stream['bitRate'] > 0:
                bitrate = '{}k'.format(stream['bitRate'])
            else:
                bitrate = 'live'
            yield bitrate, HTTPStream(self.session, stream['streamUrl'])
            stream_urls.append(stream['streamUrl'])


__plugin__ = RadioNet
