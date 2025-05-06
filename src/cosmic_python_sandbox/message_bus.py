from collections import deque
from typing import Callable, Sequence

import attrs
from attrs.validators import instance_of

from cosmic_python_sandbox.fake_logger import LoggerProtocol


@attrs.define
class Event:
    priority_event: bool = attrs.field(default=False)


EventHandlers = dict[type, Callable[[Event], Event | Sequence[Event] | None]]


@attrs.define
class MessageBus:
    event_handlers: EventHandlers = attrs.field()
    logger: LoggerProtocol = attrs.field(validator=instance_of(LoggerProtocol))
    queue: deque = attrs.field(default=attrs.Factory(deque))

    def add_events(self, events: Sequence[Event]):
        if not isinstance(events, Sequence) or not all(
            isinstance(evt, Event) for evt in events
        ):
            raise ValueError(f"{events} must be a Sequence of Event types")
        self.queue.extend(events)

    def handle_event(self):
        event = self.queue.popleft()
        self.logger.info(event)
        result = self.event_handlers[type(event)](event)

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

    def handle_events(self):
        while self.queue:
            self.handle_event()
