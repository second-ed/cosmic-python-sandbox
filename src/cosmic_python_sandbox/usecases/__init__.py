from collections.abc import Callable, Sequence

from . import events, handlers

EventHandlers = dict[type, Callable[[events.Event], events.Event | Sequence[events.Event] | None]]

EVENT_HANDLERS = {
    events.Event: handlers.example_handler,
    events.CopyFile: handlers.copy_file,
    events.MoveFile: handlers.move_file,
    events.DeleteFile: handlers.delete_file,
}
