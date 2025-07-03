import attrs

from cosmic_python_sandbox.service_layer.uow import UnitOfWorkProtocol


@attrs.define
class Event:
    priority_event: bool = attrs.field(default=False)

    @classmethod
    def from_dict(cls, msg: dict) -> "Event":
        filtered = {f.name: msg[f.name] for f in attrs.fields(cls) if f.name in msg}
        return cls(**filtered)


def example_handler(event: Event, uow: UnitOfWorkProtocol) -> None:
    with uow:
        err_msg = f"Must use a specialised event. Given {event}"
        raise ValueError(err_msg)
