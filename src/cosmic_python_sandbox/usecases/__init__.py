from collections.abc import Callable, Sequence

from ._event import Event, example_handler
from .copy_file import CopyFile, copy_file
from .delete_file import DeleteFile, delete_file
from .move_file import MoveFile, move_file

EventHandlers = dict[type, Callable[[Event], Event | Sequence[Event] | None]]

EVENT_HANDLERS = {
    Event: example_handler,
    CopyFile: copy_file,
    MoveFile: move_file,
    DeleteFile: delete_file,
}


def parse_event(msg: dict) -> Event:
    # go from most specific to least
    match msg:
        case {"action": "copy", "src": _, "dst": _}:
            return CopyFile.from_dict(msg)

        case {"action": "move", "src": _, "dst": _}:
            return MoveFile.from_dict(msg)

        case {"action": "delete", "dst": _}:
            return DeleteFile.from_dict(msg)

        case {"priority_event": _}:
            return Event.from_dict(msg)

    err_msg = f"Invalid message {msg}"
    raise ValueError(err_msg)


__all__ = [
    "EVENT_HANDLERS",
    "CopyFile",
    "DeleteFile",
    "Event",
    "EventHandlers",
    "MoveFile",
    "copy_file",
    "delete_file",
    "example_handler",
    "move_file",
    "parse_event",
]
