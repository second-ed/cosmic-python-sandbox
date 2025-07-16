from __future__ import annotations

from typing import TYPE_CHECKING

import attrs

if TYPE_CHECKING:
    from collections.abc import Sequence

    from cosmic_python_sandbox.service_layer.uow import UnitOfWorkProtocol


@attrs.define
class Event:
    priority_event: bool = attrs.field(default=False)

    @classmethod
    def from_dict(cls, msg: dict) -> Event:
        filtered = {f.name: msg[f.name] for f in attrs.fields(cls) if f.name in msg}
        return cls(**filtered)


def example_handler(event: Event, uow: UnitOfWorkProtocol) -> None:
    with uow:
        err_msg = f"Must use a specialised event. Given {event}"
        raise ValueError(err_msg)


@attrs.define
class Ok:
    event: Event | Sequence[Event] | None = attrs.field(
        default=None,
        validator=attrs.validators.optional(
            attrs.validators.or_(
                attrs.validators.instance_of(Event),
                attrs.validators.deep_iterable(attrs.validators.instance_of(Event)),
            ),
        ),
    )


@attrs.define
class Err:
    event: Event = attrs.field(validator=attrs.validators.instance_of(Event))
    error: Exception = attrs.field(validator=attrs.validators.instance_of(Exception))
    err_type: BaseException = attrs.field(init=False)
    err_msg: str = attrs.field(init=False)
    traceback: dict = attrs.field(init=False)

    def __attrs_post_init__(self) -> None:
        self.err_type = type(self.error)
        self.err_msg = str(self.error)
        self.traceback = self.error.__traceback__.tb_frame.f_locals
        self.traceback["line_no"] = self.error.__traceback__.tb_lineno
