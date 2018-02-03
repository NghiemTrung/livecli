import unittest

try:
    from unittest.mock import patch, PropertyMock
except ImportError:
    from mock import patch, PropertyMock

from livecli import Livecli
from livecli.plugins.filmon import FilmOnHLS
from livecli.stream import AkamaiHDStream
from livecli.stream import HDSStream
from livecli.stream import HLSStream
from livecli.stream import HTTPStream
from livecli.stream import RTMPStream
from livecli.stream import Stream
from livecli_cli.utils import stream_to_url


class TestStreamToURL(unittest.TestCase):
    def setUp(self):
        self.session = Livecli()

    def test_base_stream(self):
        stream = Stream(self.session)
        self.assertEqual(None, stream_to_url(stream))
        self.assertRaises(TypeError, stream.to_url)

    def test_http_stream(self):
        expected = "http://test.se/stream"
        stream = HTTPStream(self.session, expected)
        self.assertEqual(expected, stream_to_url(stream))
        self.assertEqual(expected, stream.to_url())

    def test_hls_stream(self):
        expected = "http://test.se/stream.m3u8"
        stream = HLSStream(self.session, expected)
        self.assertEqual(expected, stream_to_url(stream))
        self.assertEqual(expected, stream.to_url())

    def test_hds_stream(self):
        stream = HDSStream(self.session, "http://test.se/", "http://test.se/stream.f4m", "http://test.se/stream/1.bootstrap")
        self.assertEqual(None, stream_to_url(stream))
        self.assertRaises(TypeError, stream.to_url)

    def test_akamai_stream(self):
        stream = AkamaiHDStream(self.session, "http://akamai.test.se/stream")
        self.assertEqual(None, stream_to_url(stream))
        self.assertRaises(TypeError, stream.to_url)

    def test_rtmp_stream(self):
        stream = RTMPStream(self.session, {"rtmp": "rtmp://test.se/app/play_path",
                                           "swfVfy": "http://test.se/player.swf",
                                           "swfhash": "test",
                                           "swfsize": 123456,
                                           "playPath": "play_path"})
        expected = "rtmp://test.se/app/play_path playPath=play_path swfUrl=http://test.se/player.swf swfVfy=1"
        self.assertEqual(expected, stream_to_url(stream))
        self.assertEqual(expected, stream.to_url())

    @patch("time.time")
    @patch("livecli.plugins.filmon.FilmOnHLS.url", new_callable=PropertyMock)
    def test_filmon_stream(self, url, time):
        stream = FilmOnHLS(self.session, channel="test")
        url.return_value = "http://filmon.test.se/test.m3u8"
        stream.watch_timeout = 10
        time.return_value = 1
        expected = "http://filmon.test.se/test.m3u8"

        self.assertEqual(expected, stream_to_url(stream))
        self.assertEqual(expected, stream.to_url())

    @patch("time.time")
    @patch("livecli.plugins.filmon.FilmOnHLS.url", new_callable=PropertyMock)
    def test_filmon_expired_stream(self, url, time):
        stream = FilmOnHLS(self.session, channel="test")
        url.return_value = "http://filmon.test.se/test.m3u8"
        stream.watch_timeout = 0
        time.return_value = 1

        self.assertEqual(None, stream_to_url(stream))
        self.assertRaises(TypeError, stream.to_url)
