from typing import Callable, Sequence

from cosmic_python_sandbox.events import Event
from cosmic_python_sandbox.uow import UnitOfWorkProtocol

EventHandlers = dict[type, Callable[[Event], Event | Sequence[Event] | None]]


def example_handler(event: Event, uow: UnitOfWorkProtocol):
    with uow:
        print(event)


EVENT_HANDLERS = {Event: example_handler}
