from __future__ import print_function

import time

import base64
import random
import re

from livecli.compat import urlparse
from livecli.plugin import Plugin
from livecli.plugin.api import http
from livecli.plugin.api import useragents
from livecli.stream import HLSStream
from livecli.utils import parse_qsd
from livecli.utils.crypto import decrypt_openssl

__livecli_docs__ = {
    "domains": [
        "stream.me",
    ],
    "geo_blocked": [],
    "notes": "",
    "live": True,
    "vod": False,
    "last_update": "2017-12-23",
}


class Streann(Plugin):
    url_re = re.compile(r"https?://ott\.streann.com/streaming/player\.html")
    base_url = "https://ott.streann.com"
    get_time_url = base_url + "/web/services/public/get-server-time"
    token_url = base_url + "/loadbalancer/services/web-players/{playerId}/token/{type}/{dataId}/{deviceId}"
    stream_url = base_url + "/loadbalancer/services/web-players/{type}s-reseller/{dataId}/{playerId}/{token}/{resellerId}/playlist.m3u8?date={time}&device-type=web&device-name=web&device-os=web&device-id={deviceId}"
    passphrase_re = re.compile(r'''CryptoJS\.AES\.decrypt\(.*?,\s*(['"])(?P<passphrase>(?:(?!\1).)*)\1\s*?\);''')

    def __init__(self, url):
        super(Streann, self).__init__(url)
        self._device_id = None

    @classmethod
    def can_handle_url(cls, url):
        return cls.url_re.match(url) is not None

    @property
    def device_id(self):
        """
        Randomly generated deviceId.
        :return:
        """
        if self._device_id is None:
            self._device_id = "".join(
                random.choice("0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ") for _ in range(50))
        return self._device_id

    @property
    def time(self):
        res = http.get(self.get_time_url)
        data = http.json(res)
        return str(data.get("serverTime", int(time.time() * 1000)))

    def passphrase(self):
        res = http.get(self.url)
        passphrase_m = self.passphrase_re.search(res.text)
        return passphrase_m and passphrase_m.group("passphrase").encode("utf8")

    def get_token(self, **config):
        pdata = dict(arg1=base64.b64encode("www.ellobo106.com".encode("utf8")),
                     arg2=base64.b64encode(self.time.encode("utf8")))

        headers = {
            "User-Agent": useragents.FIREFOX,
            "Referer": self.url,
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/x-www-form-urlencoded"
        }

        res = http.post(self.token_url.format(deviceId=self.device_id, **config),
                        data=pdata, headers=headers)
        data = http.json(res)
        return data["token"]

    def _get_streams(self):
        # Get the query string
        encrypted_data = urlparse(self.url).query
        data = base64.b64decode(encrypted_data)
        # and decrypt it
        passphrase = self.passphrase()
        if passphrase:
            params = decrypt_openssl(data, passphrase)
            config = parse_qsd(params.decode("utf8"))

            return HLSStream.parse_variant_playlist(self.session,
                                                    self.stream_url.format(time=self.time,
                                                                           deviceId=self.device_id,
                                                                           token=self.get_token(**config),
                                                                           **config))


__plugin__ = Streann