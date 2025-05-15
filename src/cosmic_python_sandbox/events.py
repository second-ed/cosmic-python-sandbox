import attrs
from attrs.validators import min_len


@attrs.define
class Event:
    priority_event: bool = attrs.field(default=False)

    @classmethod
    def from_dict(cls, msg):
        filtered = {f.name: msg[f.name] for f in attrs.fields(cls) if f.name in msg}
        return cls(**filtered)


@attrs.define
class CopyFile(Event):
    src: str = attrs.field(default="", validator=[min_len(3)])
    dst: str = attrs.field(default="", validator=[min_len(3)])


@attrs.define
class MoveFile(Event):
    src: str = attrs.field(default="", validator=[min_len(3)])
    dst: str = attrs.field(default="", validator=[min_len(3)])


@attrs.define
class DeleteFile(Event):
    dst: str = attrs.field(default="", validator=[min_len(3)])


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

    raise ValueError(f"Invalid message {msg}")
