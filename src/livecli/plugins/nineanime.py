import re
from livecli.plugin import Plugin
from livecli.plugin.api import http
from livecli.plugin.api import useragents
from livecli.plugin.api import validate
from livecli.stream import HTTPStream
from livecli.compat import urlparse

__livecli_docs__ = {
    "domains": [
        "9anime.ch",
    ],
    "geo_blocked": [],
    "notes": "",
    "live": False,
    "vod": True,
    "last_update": "",
    "broken": True,
}


class NineAnime(Plugin):
    _episode_info_url = "//9anime.to/ajax/episode/info"

    _info_schema = validate.Schema({
        "grabber": validate.url(),
        "params": {
            "id": validate.text,
            "token": validate.text,
            "options": validate.text,
        }
    })

    _streams_schema = validate.Schema({
        "token": validate.text,
        "error": None,
        "data": [{
            "label": validate.text,
            "file": validate.url(),
            "type": "mp4"
        }]
    })

    _url_re = re.compile(r"https?://9anime.to/watch/(?:[^.]+?\.)(\w+)/(\w+)")

    @classmethod
    def can_handle_url(cls, url):
        return cls._url_re.match(url) is not None

    def add_scheme(self, url):
        # update the scheme for the grabber url if required
        if url.startswith("//"):
            url = "{0}:{1}".format(urlparse(self.url).scheme, url)
        return url

    def _get_streams(self):
        match = self._url_re.match(self.url)
        film_id, episode_id = match.groups()

        headers = {
            "Referer": self.url,
            "User-Agent": useragents.FIREFOX
        }

        # Get the info about the Episode, including the Grabber API URL
        info_res = http.get(self.add_scheme(self._episode_info_url),
                            params=dict(update=0, film=film_id, id=episode_id),
                            headers=headers)
        info = http.json(info_res, schema=self._info_schema)

        # Get the data about the streams from the Grabber API
        grabber_url = self.add_scheme(info["grabber"])
        stream_list_res = http.get(grabber_url, params=info["params"], headers=headers)
        stream_data = http.json(stream_list_res, schema=self._streams_schema)

        for stream in stream_data["data"]:
            yield stream["label"], HTTPStream(self.session, stream["file"])


__plugin__ = NineAnime
