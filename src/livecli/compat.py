import os
import sys

is_py2 = (sys.version_info[0] == 2)
is_py3 = (sys.version_info[0] == 3)
is_win32 = os.name == "nt"

# win/nix compatible devnull
try:
    from subprocess import DEVNULL

    def devnull():
        return DEVNULL
except ImportError:
    def devnull():
        return open(os.path.devnull, 'w')

if is_py2:
    _str = str
    str = unicode  # noqa
    range = xrange  # noqa

    def bytes(b, enc="ascii"):
        return _str(b)

elif is_py3:
    bytes = bytes
    str = str
    range = range

try:
    from urllib.parse import (
        urlparse, urlunparse, urljoin, quote, unquote, parse_qsl, urlencode
    )
    import queue
except ImportError:
    from urlparse import urlparse, urlunparse, urljoin, parse_qsl
    from urllib import quote, unquote, urlencode
    import Queue as queue

try:
    from shutil import which as compat_which
except ImportError:
    # python 2.7
    try:
        from backports.shutil_which import which as compat_which
    except ImportError:
        # Kodi - script.module.livecli
        from livecli.packages.shutil_which import which as compat_which

try:
    from Crypto.Cipher import AES as crypto_AES
    from Crypto.Cipher import Blowfish as crypto_Blowfish
    from Crypto.Cipher import PKCS1_v1_5 as crypto_PKCS1_v1_5
    from Crypto.PublicKey import RSA as crypto_RSA
    from Crypto.Util import number as crypto_number
except ImportError:
    from Cryptodome.Cipher import AES as crypto_AES
    from Cryptodome.Cipher import Blowfish as crypto_Blowfish
    from Cryptodome.Cipher import PKCS1_v1_5 as crypto_PKCS1_v1_5
    from Cryptodome.PublicKey import RSA as crypto_RSA
    from Cryptodome.Util import number as crypto_number

try:
    # python 3.4+
    from html import unescape
except ImportError:
    # python 2.7
    from HTMLParser import HTMLParser
    unescape = HTMLParser().unescape

__all__ = [
    "bytes",
    "compat_which",
    "crypto_AES",
    "crypto_Blowfish",
    "crypto_number",
    "crypto_PKCS1_v1_5",
    "crypto_RSA",
    "devnull",
    "is_py2",
    "is_py3",
    "is_win32",
    "parse_qsl",
    "queue",
    "quote",
    "range",
    "str",
    "unescape",
    "unquote",
    "urlencode",
    "urljoin",
    "urlparse",
    "urlunparse",
]
