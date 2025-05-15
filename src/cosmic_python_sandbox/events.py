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
