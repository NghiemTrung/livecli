import re

from livecli.plugin import Plugin
from livecli.plugin.plugin import parse_url_params
from livecli.stream import AkamaiHDStream
from livecli.utils import update_scheme


class AkamaiHDPlugin(Plugin):
    _url_re = re.compile(r"akamaihd://(.+)")

    @classmethod
    def can_handle_url(cls, url):
        return cls._url_re.match(url) is not None

    def _get_streams(self):
        url, params = parse_url_params(self.url)
        urlnoproto = self._url_re.match(url).group(1)
        urlnoproto = update_scheme("http://", urlnoproto)

        self.logger.debug("URL={0}; params={1}", urlnoproto, params)
        return {"live": AkamaiHDStream(self.session, urlnoproto, **params)}


__plugin__ = AkamaiHDPlugin
