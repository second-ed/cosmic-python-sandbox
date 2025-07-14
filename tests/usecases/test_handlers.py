import pytest

from cosmic_python_sandbox.adapters.logger import FakeLogger
from cosmic_python_sandbox.adapters.repo import FakeRepo
from cosmic_python_sandbox.service_layer.message_bus import (
    MessageBus,
)
from cosmic_python_sandbox.service_layer.uow import UnitOfWork
from cosmic_python_sandbox.usecases import EVENT_HANDLERS, CopyFile, DeleteFile, MoveFile


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
    fake_repo = FakeRepo(db=db)
    logger = FakeLogger()
    uow = UnitOfWork(repo=fake_repo, logger=logger, guid_func=lambda: "123-abc")
    bus = (
        MessageBus(uow=uow, event_handlers=EVENT_HANDLERS)
        .add_events(starting_events)
        .handle_events()
    )
    assert fake_repo.db == expected_db

    # make sure guids in all logs
    assert all("{'guid': '123-abc'" in log for log in bus.uow.logger.log)
