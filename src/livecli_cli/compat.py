import re
import sys

is_py2 = (sys.version_info[0] == 2)
is_py3 = (sys.version_info[0] == 3)

if is_py2:
    input = raw_input  # noqa
    stdout = sys.stdout
    file = file  # noqa
    _find_unsafe = re.compile(r"[^\w@%+=:,./-]").search

elif is_py3:
    input = input
    stdout = sys.stdout.buffer
    from io import IOBase as file
    _find_unsafe = re.compile(r"[^\w@%+=:,./-]", re.ASCII).search

try:
    from shutil import get_terminal_size as compat_get_terminal_size
except ImportError:
    # Python 2.7
    from backports.shutil_get_terminal_size import get_terminal_size as compat_get_terminal_size


def shlex_quote(s):
    """Return a shell-escaped version of the string *s*.

    Backported from Python 3.3 standard library module shlex.
    """
    if not s:
        return "''"
    if _find_unsafe(s) is None:
        return s

    # use single quotes, and put single quotes into double quotes
    # the string $'b is then quoted as '$'"'"'b'
    return "'" + s.replace("'", "'\"'\"'") + "'"


__all__ = [
    "compat_get_terminal_size",
    "file",
    "input",
    "is_py2",
    "is_py3",
    "shlex_quote",
    "stdout",
]
