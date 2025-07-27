from __future__ import annotations

import functools
from typing import TYPE_CHECKING, Any, Callable, Literal, Self, TypeVar

import attrs

T = TypeVar("T")
U = TypeVar("U")

if TYPE_CHECKING:
    from collections.abc import Sequence
    from types import TracebackType

    from cosmic_python_sandbox.service_layer.uow import UnitOfWorkProtocol


@attrs.define
class Event:
    priority_event: bool = attrs.field(default=False)

    @classmethod
    def from_dict(cls, msg: dict) -> Event:
        filtered = {f.name: msg[f.name] for f in attrs.fields(cls) if f.name in msg}
        return cls(**filtered)


@attrs.define
class Ok:
    inner: Event | Sequence[Event] | None = attrs.field(
        default=None,
        validator=attrs.validators.optional(
            attrs.validators.or_(
                attrs.validators.instance_of(Event),
                attrs.validators.deep_iterable(attrs.validators.instance_of(Event)),
            ),
        ),
    )

    def is_ok(self) -> Literal[True]:
        return True

    def is_err(self) -> Literal[False]:
        return False

    def map(self, func: Callable[[T], U]) -> Ok[U]:
        return Ok(func(self.inner))


@attrs.define
class Err:
    event: Event = attrs.field(validator=attrs.validators.instance_of(Event))
    error: Exception = attrs.field(validator=attrs.validators.instance_of(Exception))
    err_type: BaseException = attrs.field(init=False)
    err_msg: str = attrs.field(init=False)
    details: dict = attrs.field(init=False)

    def __attrs_post_init__(self) -> None:
        self.err_type = type(self.error)
        self.err_msg = str(self.error)
        self.details = self.extract_details(self.error.__traceback__)

    def extract_details(self, tb: TracebackType) -> list[dict[str, Any]]:
        trace_info = []
        while tb:
            frame = tb.tb_frame
            trace_info.append(
                {
                    "file": frame.f_code.co_filename,
                    "func": frame.f_code.co_name,
                    "line_no": tb.tb_lineno,
                    "locals": frame.f_locals,
                },
            )
            tb = tb.tb_next
        return trace_info

    def is_ok(self) -> Literal[False]:
        return False

    def is_err(self) -> Literal[True]:
        return True

    def map(self, _: Callable[[T], U]) -> Self:
        return self


Result = Ok | Err


def catch_err(func: callable) -> callable:
    @functools.wraps(func)
    def wrapper(event: Event, uow: UnitOfWorkProtocol) -> Result:
        try:
            return Ok(func(event, uow))
        except Exception as e:  # noqa: BLE001
            return Err(event, e)

    return wrapper


@catch_err
def example_handler(event: Event, uow: UnitOfWorkProtocol) -> None:
    with uow:
        err_msg = f"Must use a specialised event. Given {event}"
        raise ValueError(err_msg)
