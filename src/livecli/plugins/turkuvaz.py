import re
from livecli.plugin import Plugin
from livecli.plugin.api import http
from livecli.plugin.api import useragents
from livecli.plugin.api import validate
from livecli.stream import HLSStream

__livecli_docs__ = {
    "domains": [
        "atv.com.tr",
        "a2tv.com.tr",
        "ahaber.com.tr",
        "aspor.com.tr",
        "minikago.com.tr",
        "minikacocuk.com.tr",
    ],
    "geo_blocked": [],
    "notes": "",
    "live": True,
    "vod": False,
    "last_update": "2017-10-16",
}


class Turkuvaz(Plugin):
    """
    Plugin to support ATV/A2TV Live streams from www.atv.com.tr and www.a2tv.com.tr
    """

    _url_re = re.compile(r"""https?://(?:www.)?
                             (?:(atvavrupa).tv|
                                (atv|a2tv|ahaber|aspor|minikago|minikacocuk|anews).com.tr)
                                /webtv/(live-broadcast|canli-yayin)""",
                         re.VERBOSE)
    _hls_url = "http://trkvz-live.ercdn.net/{channel}/{channel}.m3u8"
    _token_url = "http://videotoken.tmgrup.com.tr/webtv/secure"
    _token_schema = validate.Schema(validate.all(
        {
            "Success": True,
            "Url": validate.url(),
        },
        validate.get("Url"))
    )

    @classmethod
    def can_handle_url(cls, url):
        return cls._url_re.match(url) is not None

    def _get_streams(self):
        url_m = self._url_re.match(self.url)
        domain = url_m.group(1) or url_m.group(2)
        # remap the domain to channel
        channel = {"atv": "atvhd",
                   "ahaber": "ahaberhd",
                   "aspor": "asporhd",
                   "anews": "anewshd",
                   "minikacocuk": "minikagococuk"}.get(domain, domain)
        hls_url = self._hls_url.format(channel=channel)
        # get the secure HLS URL
        res = http.get(self._token_url,
                       params="url={0}".format(hls_url),
                       headers={"Referer": self.url,
                                "User-Agent": useragents.CHROME})

        secure_hls_url = http.json(res, schema=self._token_schema)

        self.logger.debug("Found HLS URL: {0}".format(secure_hls_url))
        return HLSStream.parse_variant_playlist(self.session, secure_hls_url)


__plugin__ = Turkuvaz
