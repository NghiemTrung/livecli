# These imports, while unused, are here to provide API compatibility for this module
from livecli.utils.named_pipe import NamedPipe
from livecli.compat import is_win32

if is_win32:
    from livecli.utils.named_pipe import (
        PIPE_ACCESS_OUTBOUND,
        PIPE_TYPE_BYTE,
        PIPE_READMODE_BYTE,
        PIPE_WAIT,
        PIPE_UNLIMITED_INSTANCES,
        INVALID_HANDLE_VALUE)
