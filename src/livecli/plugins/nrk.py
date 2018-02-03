import re

from livecli.compat import urljoin
from livecli.plugin import Plugin
from livecli.plugin.api import http, validate
from livecli.stream import HLSStream

__livecli_docs__ = {
    "domains": [
        "nrk.no",
    ],
    "geo_blocked": [
        "NO",
    ],
    "notes": "",
    "live": True,
    "vod": True,
    "last_update": "2017-05-04",
}

COOKIE_PARAMS = (
    "devicetype=desktop&"
    "preferred-player-odm=hlslink&"
    "preferred-player-live=hlslink"
)

_id_re = re.compile(r"/(?:program|direkte|serie/[^/]+)/([^/]+)")
_url_re = re.compile(r"https?://(tv|radio).nrk.no/")
_api_baseurl_re = re.compile(r'''apiBaseUrl:\s*["'](?P<baseurl>[^"']+)["']''')

_schema = validate.Schema(
    validate.transform(_api_baseurl_re.search),
    validate.any(
        None,
        validate.all(
            validate.get("baseurl"),
            validate.url(
                scheme="http"
            )
        )
    )
)

_mediaelement_schema = validate.Schema({
    "mediaUrl": validate.url(
        scheme="http",
        path=validate.endswith(".m3u8")
    )
})


class NRK(Plugin):
    @classmethod
    def can_handle_url(self, url):
        return _url_re.match(url)

    def _get_streams(self):
        # Get the stream type from the url (tv/radio).
        stream_type = _url_re.match(self.url).group(1).upper()
        cookie = {
            "NRK_PLAYER_SETTINGS_{0}".format(stream_type): COOKIE_PARAMS
        }

        # Construct API URL for this program.
        baseurl = http.get(self.url, cookies=cookie, schema=_schema)
        program_id = _id_re.search(self.url).group(1)

        # Extract media URL.
        json_url = urljoin(baseurl, "mediaelement/{0}".format(program_id))
        res = http.get(json_url, cookies=cookie)
        media_element = http.json(res, schema=_mediaelement_schema)
        media_url = media_element["mediaUrl"]

        return HLSStream.parse_variant_playlist(self.session, media_url)


__plugin__ = NRK
