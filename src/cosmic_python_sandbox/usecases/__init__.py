from . import events, handlers

EVENT_HANDLERS = {
    events.Event: handlers.example_handler,
    events.CopyFile: handlers.copy_file,
    events.MoveFile: handlers.move_file,
    events.DeleteFile: handlers.delete_file,
}
