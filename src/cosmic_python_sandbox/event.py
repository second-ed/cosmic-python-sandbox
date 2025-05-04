import attrs


@attrs.define
class Event:
    priority_event: bool = attrs.field(default=False)
