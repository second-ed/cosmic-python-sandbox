from collections import deque
from collections.abc import Sequence

import attrs
from attrs.validators import instance_of

from cosmic_python_sandbox.service_layer.uow import UnitOfWorkProtocol
from cosmic_python_sandbox.usecases.events import Event
from cosmic_python_sandbox.usecases.handlers import EventHandlers


@attrs.define
class MessageBus:
    event_handlers: EventHandlers = attrs.field()
    uow: UnitOfWorkProtocol = attrs.field(validator=instance_of(UnitOfWorkProtocol))
    queue: deque = attrs.field(default=attrs.Factory(deque))

    def add_events(self, events: Sequence[Event]) -> None:
        if not isinstance(events, Sequence) or not all(isinstance(evt, Event) for evt in events):
            msg = f"{events} must be a Sequence of Event types"
            raise ValueError(msg)
        self.queue.extend(events)

    def handle_event(self) -> None:
        event = self.queue.popleft()
        result = self.event_handlers[type(event)](event, self.uow)

        if isinstance(result, Event):
            if result.priority_event:
                self.queue.appendleft(result)
            else:
                self.queue.append(result)

        elif isinstance(result, Sequence):
            front, back = [], []

            for evt in result:
                if isinstance(evt, Event):
                    if evt.priority_event:
                        front.append(evt)
                    else:
                        back.append(evt)

            if front:
                self.queue.extendleft(reversed(front))
            if back:
                self.queue.extend(back)

    def handle_events(self) -> None:
        while self.queue:
            self.handle_event()
