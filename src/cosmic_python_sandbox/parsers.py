from cosmic_python_sandbox import events


def parse_event(msg: dict) -> events.Event:
    # go from most specific to least
    match msg:
        case {"action": "copy", "src": _, "dst": _}:
            return events.CopyFile.from_dict(msg)
        case {"action": "move", "src": _, "dst": _}:
            return events.MoveFile.from_dict(msg)
        case {"action": "delete", "dst": _}:
            return events.DeleteFile.from_dict(msg)
        case {"priority_event": _}:
            return events.Event.from_dict(msg)

    raise ValueError(f"Invalid message {msg}")
