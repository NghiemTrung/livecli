import base64
import unittest

from livecli.utils.crypto import evp_bytestokey, decrypt_openssl


class TestUtil(unittest.TestCase):
    def test_evp_bytestokey(self):
        self.assertEqual((b']A@*\xbcK*v\xb9q\x9d\x91\x10\x17\xc5\x92',
                          b'(\xb4n\xd3\xc1\x11\xe8Q\x02\x90\x9b\x1c\xfbP\xea\x0f'),
                         evp_bytestokey(b"hello", b"", 16, 16))

    def test_decrpyt(self):
        # data generated with:
        #   echo "this is a test" | openssl enc -aes-256-cbc -pass pass:"livecli" -base64
        data = base64.b64decode("U2FsdGVkX19ZqpcbqkGIMTLsXunnM32Qe91+CrGtklg=")
        self.assertEqual(
            b"this is a test\n",
            decrypt_openssl(data, b"livecli")
        )
