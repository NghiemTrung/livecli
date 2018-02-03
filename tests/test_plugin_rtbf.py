import unittest

from livecli.plugins.rtbf import RTBF


class TestPluginRTBF(unittest.TestCase):
    def test_can_handle_url(self):
        should_match = [
            "https://www.rtbf.be/auvio/direct_20-02?lid=117857",
            "https://www.rtbf.be/auvio/direct_a-pleines-dents?lid=116360",
            "https://www.rtbf.be/auvio/direct_les-enquetes-de-vera?lid=116362",
        ]
        for url in should_match:
            self.assertTrue(RTBF.can_handle_url(url))

        should_not_match = [
            "https://www.rtbf.be/",
        ]
        for url in should_not_match:
            self.assertFalse(RTBF.can_handle_url(url))
