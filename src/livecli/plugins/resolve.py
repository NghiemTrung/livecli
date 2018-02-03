# -*- coding: utf-8 -*-
import re

from livecli import NoPluginError
from livecli import NoStreamsError
from livecli.cache import Cache
from livecli.compat import unquote
from livecli.compat import urljoin
from livecli.compat import urlparse
from livecli.plugin import Plugin
from livecli.plugin import PluginOptions
from livecli.plugin.api import http
from livecli.plugin.api import useragents
from livecli.plugin.plugin import HIGH_PRIORITY
from livecli.plugin.plugin import NO_PRIORITY
from livecli.stream import HDSStream
from livecli.stream import HLSStream
from livecli.stream import HTTPStream
from livecli.utils import update_scheme


class Resolve(Plugin):
    """Livecli Plugin that will try to find a validate streamurl

    Supported
        - embedded url of an already existing livecli plugin
        - website with an unencrypted fileurl in there source code
             - .m3u8
             - .f4m
             - .mp3 - only none broken urls
             - .mp4 - only none broken urls

    Unsupported
        - websites with dash, rtmp or other.
        - streams that require
            - an authentication
            - an API
        - streams that are hidden behind javascript or other encryption
        - websites with a lot of iframes
          (the blacklist feature can be used for unwanted domains)
    """

    _url_re = re.compile(r"""(resolve://)?(?P<url>.+)""")

    # Regex for: Iframes
    _iframe_re = re.compile(r"""
        <ifr(?:["']\s?\+\s?["'])?ame
        (?!\sname=["']g_iFrame).*?src=
        ["'](?P<url>[^"']+)["']
        .*?(?:/>|>(?:[^<>]+)?
        </ifr(?:["']\s?\+\s?["'])?ame(?:\s+)?>)
        """, re.VERBOSE | re.IGNORECASE)
    # Regex for: .f4m and .m3u8 files
    _playlist_re = re.compile(r"""(?:["']|=|&quot;)(?P<url>
        (?:https?:)?(?://|\\/\\/)?
            (?<!title=["'])
                [^"'<>\s\;]+\.(?:m3u8|f4m|mp3|mp4|mpd)
            (?:[^"'<>\s\\]+)?)
        (?:["']|\s|>|\\&quot;)
        """, re.DOTALL | re.VERBOSE)
    # Regex for: rtmp
    _rtmp_re = re.compile(r"""["'](?P<url>rtmp(?:e|s|t|te)?://[^"']+)["']""")
    # Regex for: .mp3 and mp4 files
    _httpstream_bitrate_re = re.compile(r"""_(?P<bitrate>\d{1,4})\.mp(?:3|4)""")
    # Regex for: streamBasePath for .f4m urls
    _stream_base_re = re.compile(r"""streamBasePath\s?(?::|=)\s?["'](?P<base>[^"']+)["']""", re.IGNORECASE)
    # Regex for: javascript redirection
    _window_location_re = re.compile(r"""<script[^<]+window\.location\.href\s?=\s?["'](?P<url>[^"']+)["'];[^<>]+""", re.DOTALL)
    _unescape_iframe_re = re.compile(r"""unescape\(["'](?P<data>%3Ciframe%20[^"']+)["']""")
    # Regex for obviously ad paths
    _ads_path = re.compile(r"""(?:/static)?/ads/?(?:\w+)?(?:\d+x\d+)?(?:_\w+)?\.(?:html?|php)""")
    options = PluginOptions({
        "blacklist_netloc": None,
        "blacklist_path": None,
    })

    def __init__(self, url):
        """Inits Resolve with default settings"""
        super(Resolve, self).__init__(url)
        self._session_attributes = Cache(filename="plugin-cache.json", key_prefix="resolve:attributes")
        self._cache_url = self._session_attributes.get("cache_url")
        if self._cache_url:
            self.referer = self._cache_url
        else:
            self.referer = self.url.replace("resolve://", "")
        self.headers = {
            "User-Agent": useragents.FIREFOX,
            "Referer": self.referer
        }

    @classmethod
    def priority(cls, url):
        """
        Returns
        - NO priority if the URL is not prefixed
        - HIGH priority if the URL is prefixed
        :param url: the URL to find the plugin priority for
        :return: plugin priority for the given URL
        """
        m = cls._url_re.match(url)
        if m:
            prefix, url = cls._url_re.match(url).groups()
            if prefix is None:
                return NO_PRIORITY
            elif prefix is not None:
                return HIGH_PRIORITY
        return NO_PRIORITY

    @classmethod
    def can_handle_url(cls, url):
        m = cls._url_re.match(url)
        if m:
            return m.group("url") is not None

    def list_in_item(self, main_item, list_of_items):
        """Check a list of items if they are in another item.
        Args:
            main_item - string that will get checked
            list_of_items - list of strings
        Returns
            True
                if a item of list_of_items in main_item
            False
                if no item of list_of_items in main_item
        """
        return any(k in main_item for k in list_of_items)

    def _make_url_list(self, old_list, base_url, stream_base=""):
        """Creates a list of validate urls from a list of broken urls
           and removes every blacklisted url

        Args:
            old_list: List of broken urls
            base_url: url that will get used for scheme and netloc
            stream_base: basically same as base_url, but used for .f4m files.

        Returns:
            List of validate urls
        """
        blacklist_netloc_user = self.get_option("blacklist_netloc")
        blacklist_netloc = (
            "about:blank",
            "adfox.ru",
            "googletagmanager.com",
            "javascript:false",
        )

        blacklist_path = [
            ("facebook.com", "/plugins"),
            ("vesti.ru", "/native_widget.html"),
        ]
        # Add --resolve-blacklist-path to blacklist_path
        blacklist_path_user = self.get_option("blacklist_path")
        if blacklist_path_user is not None:
            for _path_url in blacklist_path_user:
                if not _path_url.startswith(("http", "//")):
                    _path_url = update_scheme("http://", _path_url)
                _parsed_path_url = urlparse(_path_url)
                if _parsed_path_url.netloc and _parsed_path_url.path:
                    blacklist_path += [(_parsed_path_url.netloc, _parsed_path_url.path)]

        new_list = []
        for url in old_list:
            # Don't add the same url as self.url to the list.
            if url == self.url:
                continue
            # Repair the scheme
            new_url = url.replace("\\", "")
            if new_url.startswith("http&#58;//"):
                new_url = "http:" + new_url[9:]
            elif new_url.startswith("https&#58;//"):
                new_url = "https:" + new_url[10:]
            # Repair the domain
            if stream_base and new_url[1] is not "/":
                if new_url[0] is "/":
                    new_url = new_url[1:]
                new_url = urljoin(stream_base, new_url)
            else:
                new_url = urljoin(base_url, new_url)
            # Parse the url and remove not wanted urls
            parse_new_url = urlparse(new_url)
            REMOVE = False
            # Removes blacklisted domains
            if REMOVE is False and parse_new_url.netloc.endswith(blacklist_netloc):
                REMOVE = True
            # Removes blacklisted domains from --resolve-blacklist-netloc
            if REMOVE is False and blacklist_netloc_user is not None and parse_new_url.netloc.endswith(tuple(blacklist_netloc_user)):
                REMOVE = True
            # Removes blacklisted paths from a domain
            if REMOVE is False:
                for netloc, path in blacklist_path:
                    if parse_new_url.netloc.endswith(netloc) and parse_new_url.path.startswith(path):
                        REMOVE = True
                        continue
            # Removes images and chatrooms
            if REMOVE is False and parse_new_url.path.endswith((".jpg", ".png", ".svg", "/chat")):
                REMOVE = True
            # Remove obviously ad urls
            if REMOVE is False and self._ads_path.match(parse_new_url.path):
                REMOVE = True
            if REMOVE is True:
                self.logger.debug("Removed url: {0}".format(new_url))
                continue
            # Add url to the list
            new_list += [new_url]
        # Remove duplicates
        new_list = list(set(new_list))
        return new_list

    def _cache_self_url(self):
        """Cache self.url

        Raises:
            NoPluginError: if self.url is the same as self._cache_url
        """
        # TODO: use a list of all used urls
        #       and remove the urls with self._make_url_list
        # this is now useless for one url check
        # because self._make_url_list will remove self.url
        if self._cache_url == self.url:
            self.logger.debug("Abort: Website is already in cache.")
            raise NoPluginError

        """ set a 5 sec cache to avoid loops with the same url """
        self.logger.debug("Old cache: {0}".format(self._session_attributes.get("cache_url")))
        self._session_attributes.set("cache_url", self.url, expires=5)
        self.logger.debug("New cache: {0}".format(self._session_attributes.get("cache_url")))
        return

    def _iframe_src(self, res):
        """Tries to find every iframe url,
           it will use the first iframe as self.url,
           but every other url can will be shown in the terminal.

        Args:
            res: Content from self._res_text

        Returns:
            True
                if self.url was changed with an iframe url.
            None
                if no iframe was found.
        """
        iframe_all = self._iframe_re.findall(res)

        # Fallback for unescape('%3Ciframe%20
        unescape_iframe = self._unescape_iframe_re.findall(res)
        if unescape_iframe:
            unescape_text = []
            for data in unescape_iframe:
                unescape_text += [unquote(data)]
            unescape_text = ",".join(unescape_text)
            unescape_iframe = self._iframe_re.findall(unescape_text)
            if unescape_iframe:
                iframe_all = iframe_all + unescape_iframe

        if iframe_all:
            iframe_list = self._make_url_list(iframe_all, self.url)
            if iframe_list:
                self.logger.info("Found iframes: {0}".format(", ".join(iframe_list)))
                self.url = iframe_list[0]
                return True
        return None

    def _window_location(self, res):
        """Tries to find a script with window.location.href

        Args:
            res: Content from self._res_text

        Returns:
            True
                if self.url was changed.
            None
                if no url was found.
        """

        match = self._window_location_re.search(res)
        if match:
            self.url = match.group("url")
            return True
        return None

    def _resolve_playlist(self, res, playlist_all):
        """ yield for _resolve_res

        Args:
            res: Content from self._res_text
            playlist_all: List of streams

        Returns:
            yield every stream
        """
        # m_base is used for .f4m files that doesn't have a base_url
        m_base = self._stream_base_re.search(res)
        if m_base:
            stream_base = m_base.group("base")
        else:
            stream_base = ""

        playlist_list = self._make_url_list(playlist_all, self.url, stream_base)
        self.logger.debug("Found URL: {0}".format(", ".join(playlist_list)))
        endswith_blacklist = (".mp3", ".mp4", ".vtt")
        for url in playlist_list:
            if ".m3u8" in url and not url.endswith(endswith_blacklist):
                try:
                    streams = HLSStream.parse_variant_playlist(self.session, url, headers=self.headers).items()
                    if not streams:
                        yield "live", HLSStream(self.session, url, headers=self.headers)
                    for s in streams:
                        yield s
                except Exception:
                    self.logger.error("Skipping hls_url: {0}".format(url))
            elif ".f4m" in url and not url.endswith(endswith_blacklist):
                try:
                    for s in HDSStream.parse_manifest(self.session, url, headers=self.headers).items():
                        yield s
                except Exception:
                    self.logger.error("Skipping hds_url: {0}".format(url))
            elif self.list_in_item(url, [".mp3", ".mp4"]) and not self.list_in_item(url, [".f4m", ".m3u8", ".mpd"]):
                try:
                    name = "live"
                    m = self._httpstream_bitrate_re.search(url)
                    if m:
                        name = "{0}k".format(m.group("bitrate"))
                    yield name, HTTPStream(self.session, url, headers=self.headers)
                except Exception:
                    self.logger.error("Skipping http_url: {0}".format(url))
            elif ".mpd" in url and not url.endswith(endswith_blacklist):
                try:
                    self.logger.info("Found mpd: {0}".format(url))
                except Exception:
                    self.logger.error("Skipping mpd_url: {0}".format(url))

    def _resolve_res(self, res):
        """Tries to find every .f4m or .m3u8 url on this website,
           it will try to add every url that was found as a stream.

        Args:
            res: Content from self._res_text

        Returns:
            True
              - if stream got added
            False
              - if no stream got added
        """
        playlist_all = self._playlist_re.findall(res)

        # experimental rtmp search, will only print the url.
        m_rtmp = self._rtmp_re.search(res)
        if m_rtmp:
            self.logger.info("Found RTMP: {0}".format(m_rtmp.group("url")))

        if playlist_all:
            for url in playlist_all:
                if self.list_in_item(url, [".jpg", ".png"]):
                    playlist_all.remove(url)
            if playlist_all:
                return self._resolve_playlist(res, playlist_all)
        return False

    def _res_text(self, url):
        """Content of a website

        Args:
            url: URL with an embedded Video Player.

        Returns:
            Content of the response
        """
        try:
            res = http.get(url, headers=self.headers, allow_redirects=True)
        except Exception as e:
            if "Received response with content-encoding: gzip" in str(e):
                headers = {
                    "User-Agent": useragents.FIREFOX,
                    "Referer": self.referer,
                    "Accept-Encoding": "deflate"
                }
                res = http.get(url, headers=headers, allow_redirects=True)
            elif "403 Client Error" in str(e):
                self.logger.error("Website Access Denied/Forbidden, you might be geo-blocked or other params are missing.")
                raise NoStreamsError(self.url)
            elif "404 Client Error" in str(e):
                self.logger.error("Website was not found, the link is broken or dead.")
                raise NoStreamsError(self.url)
            else:
                raise e

        if res.history:
            for resp in res.history:
                self.logger.debug("Redirect: {0} - {1}".format(resp.status_code, resp.url))
            self.logger.debug("URL: {0}".format(res.url))
        return res.text

    def _get_streams(self):
        """Tries to find streams.

        Returns:
            Playable video from self._resolve_res
                or
            New self.url for livecli
        Raises:
            NoPluginError: if no video was found.
        """
        self.url = self.url.replace("resolve://", "")
        self._cache_self_url()
        self.url = update_scheme("http://", self.url)

        """ GET website content """
        o_res = self._res_text(self.url)

        """ HLS or HDS stream """
        x = self._resolve_res(o_res)
        if x:
            return x

        """ iframe url """
        x = self._iframe_src(o_res)

        if not x:
            """ script window.location.href """
            x = self._window_location(o_res)

        if x:
            return self.session.streams(self.url)

        raise NoPluginError


__plugin__ = Resolve
