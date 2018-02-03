import unittest

import pytest
from mock import patch
from livecli import StreamError
from livecli import Livecli
from livecli.stream import StreamProcess


@pytest.mark.parametrize("parameters,arguments,expected", [
    (dict(h=True), None, ["test", "-h"]),
    (dict(foo="bar"), None, ["test", "--foo", "bar"]),
    (dict(L="big"), None, ["test", "-L", "big"]),
    (None, ["foo", "bar"], ["test", "foo", "bar"]),
    (dict(extra="nothing", verbose=True, L="big"), None, ["test", "-L", "big", "--extra", "nothing", "--verbose"]),
    (dict(extra=["a", "b", "c"]), None, ["test", "--extra", "a", "--extra", "b", "--extra", "c"]),
    (dict(e=["a", "b", "c"]), None, ["test", "-e", "a", "-e", "b", "-e", "c"]),
])
def test_bake(parameters, arguments, expected):
    assert expected == StreamProcess.bake("test", parameters or {}, arguments or [])


class TestStreamProcess(unittest.TestCase):

    def test_bake_different_prefix(self):
        self.assertEqual(["test", "/H", "/foo", "bar", "/help"],
                         StreamProcess.bake("test", dict(help=True, H=True, foo="bar"),
                                            long_option_prefix="/", short_option_prefix="/"))

        self.assertEqual(["test", "/?"],
                         StreamProcess.bake("test", {"?": True},
                                            long_option_prefix="/", short_option_prefix="/"))

    def test_check_cmd_none(self):
        s = StreamProcess(Livecli())
        self.assertRaises(StreamError, s._check_cmd)

    @patch('livecli.stream.streamprocess.compat_which')
    def test_check_cmd_cat(self, compat_which):
        s = StreamProcess(Livecli())
        compat_which.return_value = s.cmd = "test"
        self.assertEqual("test", s._check_cmd())

    @patch('livecli.stream.streamprocess.compat_which')
    def test_check_cmd_nofound(self, compat_which):
        s = StreamProcess(Livecli())
        s.cmd = "test"
        compat_which.return_value = None
        self.assertRaises(StreamError, s._check_cmd)

    @patch('livecli.stream.streamprocess.compat_which')
    def test_check_cmdline(self, compat_which):
        s = StreamProcess(Livecli(), params=dict(help=True))
        compat_which.return_value = s.cmd = "test"
        self.assertEqual("test --help", s.cmdline())

    @patch('livecli.stream.streamprocess.compat_which')
    def test_check_cmdline_long(self, compat_which):
        s = StreamProcess(Livecli(), params=dict(out_file="test file.txt"))
        compat_which.return_value = s.cmd = "test"
        self.assertEqual("test --out-file \"test file.txt\"", s.cmdline())
