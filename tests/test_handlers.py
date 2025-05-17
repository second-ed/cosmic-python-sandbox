import pytest

from cosmic_python_sandbox.events import CopyFile, DeleteFile, MoveFile
from cosmic_python_sandbox.handlers import EVENT_HANDLERS
from cosmic_python_sandbox.io_mod import FakeIO
from cosmic_python_sandbox.logger import FakeLogger
from cosmic_python_sandbox.message_bus import (
    MessageBus,
)
from cosmic_python_sandbox.uow import UnitOfWork


@pytest.fixture
def db():
    return {
        "some_filepath1.py": "import this",
        "some_filepath2.sh": "echo blah",
    }

    #     MoveFile(src="some_filepath2.sh", dst="better_bash_name.sh"),
    # DeleteFile(dst="some_filepath1.py")


@pytest.mark.parametrize(
    "starting_events, expected_db, expected_log",
    (
        pytest.param(
            [
                CopyFile(src="some_filepath1.py", dst="another_filepath2.py"),
            ],
            {
                "some_filepath1.py": "import this",
                "another_filepath2.py": "import this",
                "some_filepath2.sh": "echo blah",
            },
            [],
        ),
        pytest.param(
            [
                MoveFile(src="some_filepath1.py", dst="another_filepath2.py"),
            ],
            {
                "another_filepath2.py": "import this",
                "some_filepath2.sh": "echo blah",
            },
            [],
        ),
        pytest.param(
            [
                DeleteFile(dst="some_filepath2.sh"),
            ],
            {
                "some_filepath1.py": "import this",
            },
            [],
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
            [],
        ),
    ),
)
def test_handler(db, starting_events, expected_db, expected_log):
    fake_io = FakeIO(db)
    logger = FakeLogger()
    uow = UnitOfWork(repo=fake_io, logger=logger)
    bus = MessageBus(uow=uow, event_handlers=EVENT_HANDLERS)
    bus.add_events(starting_events)
    bus.handle_events()
    assert fake_io.db == expected_db
    # assert bus.uow.logger.log == expected_log
