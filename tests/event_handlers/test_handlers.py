import pytest

from cosmic_python_sandbox.adapters.io_mod import FakeIO
from cosmic_python_sandbox.adapters.logger import FakeLogger
from cosmic_python_sandbox.event_handlers.events import CopyFile, DeleteFile, MoveFile
from cosmic_python_sandbox.event_handlers.handlers import EVENT_HANDLERS
from cosmic_python_sandbox.service_layer.message_bus import (
    MessageBus,
)
from cosmic_python_sandbox.service_layer.uow import UnitOfWork


@pytest.fixture
def db() -> dict[str, str]:
    return {
        "some_filepath1.py": "import this",
        "some_filepath2.sh": "echo blah",
    }


@pytest.mark.parametrize(
    ("starting_events", "expected_db"),
    [
        pytest.param(
            [
                CopyFile(src="some_filepath1.py", dst="another_filepath2.py"),
            ],
            {
                "some_filepath1.py": "import this",
                "another_filepath2.py": "import this",
                "some_filepath2.sh": "echo blah",
            },
        ),
        pytest.param(
            [
                MoveFile(src="some_filepath1.py", dst="another_filepath2.py"),
            ],
            {
                "another_filepath2.py": "import this",
                "some_filepath2.sh": "echo blah",
            },
        ),
        pytest.param(
            [
                DeleteFile(dst="some_filepath2.sh"),
            ],
            {
                "some_filepath1.py": "import this",
            },
        ),
        pytest.param(
            [
                CopyFile(src="some_filepath1.py", dst="another_filepath2.py"),
                MoveFile(src="some_filepath2.sh", dst="better_name.sh"),
                DeleteFile(dst="another_filepath2.py"),
            ],
            {
                "some_filepath1.py": "import this",
                "better_name.sh": "echo blah",
            },
        ),
    ],
)
def test_handler(db, starting_events, expected_db):
    fake_io = FakeIO(db)
    logger = FakeLogger()
    uow = UnitOfWork(repo=fake_io, logger=logger)
    bus = MessageBus(uow=uow, event_handlers=EVENT_HANDLERS)
    bus.add_events(starting_events)
    bus.handle_events()
    assert fake_io.db == expected_db

    # make sure guids in all logs
    assert all("{'guid': " in log for log in bus.uow.logger.log)
