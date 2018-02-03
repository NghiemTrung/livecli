import json
import re
import zlib

try:
    import xml.etree.cElementTree as ET
except ImportError:  # pragma: no cover
    import xml.etree.ElementTree as ET

from livecli.compat import urljoin, urlparse, parse_qsl, is_py2, urlunparse
from livecli.exceptions import PluginError
from livecli.utils.named_pipe import NamedPipe


def swfdecompress(data):
    if data[:3] == b"CWS":
        data = b"F" + data[1:8] + zlib.decompress(data[8:])

    return data


def verifyjson(json, key):
    if not isinstance(json, dict):
        raise PluginError("JSON result is not a dict")

    if key not in json:
        raise PluginError("Missing '{0}' key in JSON".format(key))

    return json[key]


def absolute_url(baseurl, url):
    if not url.startswith("http"):
        return urljoin(baseurl, url)
    else:
        return url


def prepend_www(url):
    """Changes google.com to www.google.com"""
    parsed = urlparse(url)
    if parsed.netloc.split(".")[0] != "www":
        return parsed.scheme + "://www." + parsed.netloc + parsed.path
    else:
        return url


def parse_json(data, name="JSON", exception=PluginError, schema=None):
    """Wrapper around json.loads.

    Wraps errors in custom exception with a snippet of the data in the message.
    """
    try:
        json_data = json.loads(data)
    except ValueError as err:
        snippet = repr(data)
        if len(snippet) > 35:
            snippet = snippet[:35] + " ..."
        else:
            snippet = data

        raise exception("Unable to parse {0}: {1} ({2})".format(name, err, snippet))

    if schema:
        json_data = schema.validate(json_data, name=name, exception=exception)

    return json_data


def parse_xml(data, name="XML", ignore_ns=False, exception=PluginError, schema=None):
    """Wrapper around ElementTree.fromstring with some extras.

    Provides these extra features:
     - Handles incorrectly encoded XML
     - Allows stripping namespace information
     - Wraps errors in custom exception with a snippet of the data in the message
    """
    if is_py2 and isinstance(data, unicode):  # noqa
        data = data.encode("utf8")

    if ignore_ns:
        data = re.sub(" xmlns=\"(.+?)\"", "", data)

    try:
        tree = ET.fromstring(data)
    except Exception as err:
        snippet = repr(data)
        if len(snippet) > 35:
            snippet = snippet[:35] + " ..."

        raise exception("Unable to parse {0}: {1} ({2})".format(name, err, snippet))

    if schema:
        tree = schema.validate(tree, name=name, exception=exception)

    return tree


def parse_qsd(data, name="query string", exception=PluginError, schema=None, **params):
    """Parses a query string into a dict.

    Unlike parse_qs and parse_qsl, duplicate keys are not preserved in
    favor of a simpler return value.
    """

    value = dict(parse_qsl(data, **params))
    if schema:
        value = schema.validate(value, name=name, exception=exception)

    return value


def rtmpparse(url):
    parse = urlparse(url)
    netloc = "{hostname}:{port}".format(hostname=parse.hostname,
                                        port=parse.port or 1935)
    split = list(filter(None, parse.path.split("/")))
    playpath = None
    if len(split) > 2:
        app = "/".join(split[:2])
        playpath = "/".join(split[2:])
    elif len(split) == 2:
        app, playpath = split
    else:
        app = split[0]

    if len(parse.query) > 0:
        playpath += "?{parse.query}".format(parse=parse)

    tcurl = "{scheme}://{netloc}/{app}".format(scheme=parse.scheme,
                                               netloc=netloc,
                                               app=app)

    return tcurl, playpath


def update_scheme(current, target):
    """
    Take the scheme from the current URL and applies it to the
    target URL if the target URL startswith // or is missing a scheme
    :param current: current URL
    :param target: target URL
    :return: target URL with the current URLs scheme
    """
    target_p = urlparse(target)
    if not target_p.scheme and target_p.netloc:
        return "{0}:{1}".format(urlparse(current).scheme,
                                urlunparse(target_p))
    elif not target_p.scheme and not target_p.netloc:
        return "{0}://{1}".format(urlparse(current).scheme,
                                  urlunparse(target_p))
    else:
        return target


def time_to_offset(t):
    """
    converts hours minutes seconds to seconds
    :param value: 01h22m33s
    :return: seconds
    """
    _time_re = re.compile(r"""
        (?:
            (?P<hours>\d+)h
        )?
        (?:
            (?P<minutes>\d+)m
        )?
        (?:
            (?P<seconds>\d+)s
        )?
    """, re.VERBOSE)

    match = _time_re.match(t)
    if match:
        offset = int(match.group("hours") or "0") * 60 * 60
        offset += int(match.group("minutes") or "0") * 60
        offset += int(match.group("seconds") or "0")
    else:
        offset = 0

    return offset


def hours_minutes_seconds(value):
    """
    converts hours:minutes:seconds to seconds
    :param value: hh:mm:ss
    :return: seconds
    """
    _hours_minutes_seconds_re = re.compile(r"-?(?P<hours>\d+):(?P<minutes>\d+):(?P<seconds>\d+)")
    match = _hours_minutes_seconds_re.match(value)
    if not match:
        raise ValueError
    s = 0
    s += int(match.group("hours")) * 60 * 60
    s += int(match.group("minutes")) * 60
    s += int(match.group("seconds"))

    return s


def escape_librtmp(value):
    if isinstance(value, bool):
        value = "1" if value else "0"
    if isinstance(value, int):
        value = str(value)

    # librtmp expects some characters to be escaped
    value = value.replace("\\", "\\5c")
    value = value.replace(" ", "\\20")
    value = value.replace('"', "\\22")
    return value


__all__ = [
    "absolute_url",
    "escape_librtmp",
    "NamedPipe",
    "parse_json",
    "parse_qsd",
    "parse_xml",
    "prepend_www",
    "rtmpparse",
    "swfdecompress",
    "time_to_offset",
    "verifyjson",
]
