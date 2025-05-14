from contextlib import nullcontext as does_not_raise

import attrs
import pytest

from src.cosmic_python_sandbox.handlers import EVENT_HANDLERS
from src.cosmic_python_sandbox.io_mod import FakeIO
from src.cosmic_python_sandbox.logger import FakeLogger
from src.cosmic_python_sandbox.message_bus import (
    Event,
    MessageBus,
)
from src.cosmic_python_sandbox.uow import UnitOfWork, UnitOfWorkProtocol


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


def handle_event1(event: Event, uow: UnitOfWorkProtocol):
    return SomeEvent2()


def handle_event2(event: Event, uow: UnitOfWorkProtocol):
    return SomeEvent3()


def handle_event3(event: Event, uow: UnitOfWorkProtocol):
    return SomeEvent4()


def handle_event4(event: Event, uow: UnitOfWorkProtocol):
    with uow:
        uow.repo.write("abc.ext", [1, 2, 3])
        assert uow.repo.read("abc.ext", "ext") == [1, 2, 3]


def handle_event2_priority(event: Event, uow: UnitOfWorkProtocol):
    return [SomeEvent3(), SomeEvent4(True)]


def handle_event3_priority(event: Event, uow: UnitOfWorkProtocol):
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
                "INFO: {'guid': '123-abc', 'msg': 'Initialising UOW'}",
                "INFO: {'guid': '123-abc', 'msg': 'Completed UOW'}",
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
                "INFO: {'guid': '123-abc', 'msg': 'Initialising UOW'}",
                "INFO: {'guid': '123-abc', 'msg': 'Completed UOW'}",
                "INFO: SomeEvent3(priority_event=False)",
                "INFO: SomeEvent4(priority_event=True)",
                "INFO: {'guid': '123-abc', 'msg': 'Initialising UOW'}",
                "INFO: {'guid': '123-abc', 'msg': 'Completed UOW'}",
            ],
            does_not_raise(),
            id="Ensure simple priority queue is executed correctly",
        ),
        pytest.param(
            EVENT_HANDLERS,
            [Event()],
            [
                "INFO: Event(priority_event=False)",
                "INFO: {'guid': '123-abc', 'msg': 'Initialising UOW'}",
                "INFO: {'guid': '123-abc', 'msg': 'Completed UOW'}",
            ],
            does_not_raise(),
            id="Ensure single queue is executed correctly",
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
    def fixed_guid():
        return "123-abc"

    with expected_context:
        fake_io = FakeIO()
        logger = FakeLogger()
        uow = UnitOfWork(repo=fake_io, logger=logger, guid_generator=fixed_guid)
        bus = MessageBus(uow=uow, event_handlers=handlers)
        bus.add_events(starting_events)
        bus.handle_events()
        bus.uow.logger.log == expected_log
