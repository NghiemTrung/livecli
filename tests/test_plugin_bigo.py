import unittest

from livecli.plugins.bigo import Bigo


class TestPluginBigo(unittest.TestCase):
    def test_can_handle_url(self):
        # Correct urls
        self.assertTrue(Bigo.can_handle_url("http://bigo.tv/00000000"))
        self.assertTrue(Bigo.can_handle_url("https://bigo.tv/00000000"))
        self.assertTrue(Bigo.can_handle_url("https://www.bigo.tv/00000000"))
        self.assertTrue(Bigo.can_handle_url("http://www.bigo.tv/00000000"))
        self.assertTrue(Bigo.can_handle_url("http://www.bigo.tv/fancy1234"))

        # Old URLs
        self.assertFalse(Bigo.can_handle_url("http://www.bigoweb.co/show/00000000"))
        self.assertFalse(Bigo.can_handle_url("https://www.bigoweb.co/show/00000000"))
        self.assertFalse(Bigo.can_handle_url("http://bigoweb.co/show/00000000"))
        self.assertFalse(Bigo.can_handle_url("https://bigoweb.co/show/00000000"))


if __name__ == "__main__":
    unittest.main()
