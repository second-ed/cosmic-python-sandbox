from contextlib import contextmanager
from contextlib import nullcontext as does_not_raise

import attrs
import pytest

from cosmic_python_sandbox.adapters.clock import fake_clock_now
from cosmic_python_sandbox.adapters.io_wrappers._io_protocol import FileType
from cosmic_python_sandbox.adapters.logger import FakeLogger
from cosmic_python_sandbox.adapters.repo import FakeRepo
from cosmic_python_sandbox.service_layer.message_bus import (
    MessageBus,
)
from cosmic_python_sandbox.service_layer.uow import UnitOfWork, UnitOfWorkProtocol
from cosmic_python_sandbox.usecases import EVENT_HANDLERS, Event


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


def handle_event1(event: Event, uow: UnitOfWorkProtocol) -> Event:
    with uow:
        uow.logger.info({"guid": uow.guid, "event": event})
    return SomeEvent2()


def handle_event2(event: Event, uow: UnitOfWorkProtocol) -> Event:
    with uow:
        uow.logger.info({"guid": uow.guid, "event": event})
    return SomeEvent3()


def handle_event3(event: Event, uow: UnitOfWorkProtocol) -> Event:
    with uow:
        uow.logger.info({"guid": uow.guid, "event": event})
    return SomeEvent4()


def handle_event4(event: Event, uow: UnitOfWorkProtocol) -> None:
    with uow:
        uow.repo.io.write("abc.ext", [1, 2, 3], FileType.PARQUET)
        assert uow.repo.io.read("abc.ext", FileType.PARQUET) == [1, 2, 3]


def handle_event2_priority(event: Event, uow: UnitOfWorkProtocol) -> list[Event]:
    with uow:
        uow.logger.info({"guid": uow.guid, "event": event})
    return [SomeEvent3(), SomeEvent4(priority_event=True)]


def handle_event3_priority(event: Event, uow: UnitOfWorkProtocol) -> Event:
    with uow:
        uow.logger.info({"guid": uow.guid, "event": event})
    return SomeEvent4(priority_event=True)


@pytest.mark.parametrize(
    ("handlers", "starting_events", "expected_log", "expected_context"),
    [
        pytest.param(
            {
                SomeEvent1: handle_event1,
                SomeEvent2: handle_event2,
                SomeEvent3: handle_event3,
                SomeEvent4: handle_event4,
            },
            [SomeEvent1()],
            [
                "INFO: {'guid': '123-abc', 'start_time': '20250527_194000', 'msg': 'Initialising UOW'}",
                "INFO: {'guid': '123-abc', 'event': SomeEvent1(priority_event=False)}",
                "INFO: {'guid': '123-abc', 'end_time': '20250527_194000', 'msg': 'Completed UOW'}",
                "INFO: {'guid': '123-abc', 'start_time': '20250527_194000', 'msg': 'Initialising UOW'}",
                "INFO: {'guid': '123-abc', 'event': SomeEvent2(priority_event=False)}",
                "INFO: {'guid': '123-abc', 'end_time': '20250527_194000', 'msg': 'Completed UOW'}",
                "INFO: {'guid': '123-abc', 'start_time': '20250527_194000', 'msg': 'Initialising UOW'}",
                "INFO: {'guid': '123-abc', 'event': SomeEvent3(priority_event=False)}",
                "INFO: {'guid': '123-abc', 'end_time': '20250527_194000', 'msg': 'Completed UOW'}",
                "INFO: {'guid': '123-abc', 'start_time': '20250527_194000', 'msg': 'Initialising UOW'}",
                "INFO: {'guid': '123-abc', 'end_time': '20250527_194000', 'msg': 'Completed UOW'}",
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
                "INFO: {'guid': '123-abc', 'start_time': '20250527_194000', 'msg': 'Initialising UOW'}",
                "INFO: {'guid': '123-abc', 'event': SomeEvent2(priority_event=False)}",
                "INFO: {'guid': '123-abc', 'end_time': '20250527_194000', 'msg': 'Completed UOW'}",
                "INFO: {'guid': '123-abc', 'start_time': '20250527_194000', 'msg': 'Initialising UOW'}",
                "INFO: {'guid': '123-abc', 'end_time': '20250527_194000', 'msg': 'Completed UOW'}",
                "INFO: {'guid': '123-abc', 'start_time': '20250527_194000', 'msg': 'Initialising UOW'}",
                "INFO: {'guid': '123-abc', 'event': SomeEvent3(priority_event=False)}",
                "INFO: {'guid': '123-abc', 'end_time': '20250527_194000', 'msg': 'Completed UOW'}",
                "INFO: {'guid': '123-abc', 'start_time': '20250527_194000', 'msg': 'Initialising UOW'}",
                "INFO: {'guid': '123-abc', 'end_time': '20250527_194000', 'msg': 'Completed UOW'}",
            ],
            does_not_raise(),
            id="Ensure simple priority queue is executed correctly",
        ),
        pytest.param(
            EVENT_HANDLERS,
            [Event()],
            [
                "INFO: {'guid': '123-abc', 'start_time': '20250527_194000', 'msg': 'Initialising UOW'}",
                "ERROR: {'guid': '123-abc', 'end_time': '20250527_194000', 'msg': ValueError('Must use a specialised event. Given Event(priority_event=False)')}",
            ],
            pytest.raises(ValueError),
            id="Ensure single queue is executed correctly",
        ),
        pytest.param(
            {
                SomeEvent1: handle_event1,
            },
            [1],
            [],
            pytest.raises(ValueError),
            id="Ensure raises ValueError when given invalid events",
        ),
    ],
)
def test_message_bus(
    handlers: dict,
    starting_events: list,
    expected_log: list,
    expected_context: contextmanager,
) -> None:
    def fixed_guid() -> str:
        return "123-abc"

    with expected_context:
        fake_repo = FakeRepo()
        logger = FakeLogger()
        uow = UnitOfWork(
            repo=fake_repo,
            logger=logger,
            guid_func=fixed_guid,
            clock_func=fake_clock_now,
        )
        bus = MessageBus(uow=uow, event_handlers=handlers)
        bus.add_events(starting_events).handle_events()

    assert bus.uow.logger.log == expected_log
