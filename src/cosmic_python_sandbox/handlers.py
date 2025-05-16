from typing import Callable, Sequence

from cosmic_python_sandbox.events import CopyFile, DeleteFile, Event, MoveFile
from cosmic_python_sandbox.uow import UnitOfWorkProtocol

EventHandlers = dict[type, Callable[[Event], Event | Sequence[Event] | None]]


def example_handler(event: Event, uow: UnitOfWorkProtocol):
    with uow:
        print(event)


def copy_file(event: CopyFile, uow: UnitOfWorkProtocol):
    with uow:
        uow.repo.copy(event.src, event.dst)


def move_file(event: MoveFile, uow: UnitOfWorkProtocol):
    with uow:
        uow.repo.move(event.src, event.dst)


def delete_file(event: DeleteFile, uow: UnitOfWorkProtocol):
    with uow:
        uow.repo.delete(event.dst)


EVENT_HANDLERS = {
    Event: example_handler,
    CopyFile: copy_file,
    MoveFile: move_file,
    DeleteFile: delete_file,
}
