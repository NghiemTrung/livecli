import unittest

from livecli.plugins.okru import OKru


class TestPluginOKru(unittest.TestCase):
    def test_can_handle_url(self):
        should_match = [
            "https://www.ok.ru/live/73314",
            "https://www.ok.ru/video/549049207439",
        ]
        for url in should_match:
            self.assertTrue(OKru.can_handle_url(url))

        should_not_match = [
            "https://www.ok.ru",
        ]
        for url in should_not_match:
            self.assertFalse(OKru.can_handle_url(url))
