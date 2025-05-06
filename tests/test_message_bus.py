from contextlib import nullcontext as does_not_raise

import attrs
import pytest

from src.cosmic_python_sandbox.fake_logger import FakeLogger
from src.cosmic_python_sandbox.message_bus import Event, MessageBus


@attrs.define
class SomeEvent1(Event):
    pass


@attrs.define
class SomeEvent2(Event):
    pass


@attrs.define
class SomeEvent3(Event):
    pass


@attrs.define
class SomeEvent4(Event):
    pass


def handle_event1(event):
    return SomeEvent2()


def handle_event2(event):
    return SomeEvent3()


def handle_event3(event):
    return SomeEvent4()


def handle_event4(event):
    pass


def handle_event2_priority(event):
    return [SomeEvent3(), SomeEvent4(True)]


def handle_event3_priority(event):
    return SomeEvent4(True)


@pytest.mark.parametrize(
    "handlers, starting_events, expected_log, expected_context",
    (
        pytest.param(
            {
                SomeEvent1: handle_event1,
                SomeEvent2: handle_event2,
                SomeEvent3: handle_event3,
                SomeEvent4: handle_event4,
            },
            [SomeEvent1()],
            [
                "INFO: SomeEvent1(priority_event=False)",
                "INFO: SomeEvent2(priority_event=False)",
                "INFO: SomeEvent3(priority_event=False)",
                "INFO: SomeEvent4(priority_event=False)",
            ],
            does_not_raise(),
            id="Ensure simple linear queue is executed correctly",
        ),
        pytest.param(
            {
                SomeEvent1: handle_event1,
                SomeEvent2: handle_event2_priority,
                SomeEvent3: handle_event3_priority,
                SomeEvent4: handle_event4,
            },
            [SomeEvent2()],
            [
                "INFO: SomeEvent2(priority_event=False)",
                "INFO: SomeEvent4(priority_event=True)",
                "INFO: SomeEvent3(priority_event=False)",
                "INFO: SomeEvent4(priority_event=True)",
            ],
            does_not_raise(),
            id="Ensure simple priority queue is executed correctly",
        ),
        pytest.param(
            {
                SomeEvent1: handle_event1,
            },
            [1],
            None,
            pytest.raises(ValueError),
            id="Ensure raises ValueError when given invalid events",
        ),
    ),
)
def test_message_bus(handlers, starting_events, expected_log, expected_context):
    with expected_context:
        logger = FakeLogger()
        bus = MessageBus(event_handlers=handlers, logger=logger)
        bus.add_events(starting_events)
        bus.handle_events()
        bus.logger.log == expected_log
