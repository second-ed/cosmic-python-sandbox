from typing import Callable, Sequence

from cosmic_python_sandbox.events import CopyFile, DeleteFile, Event, MoveFile
from cosmic_python_sandbox.uow import UnitOfWorkProtocol

EventHandlers = dict[type, Callable[[Event], Event | Sequence[Event] | None]]


def example_handler(event: Event, uow: UnitOfWorkProtocol):
    with uow:
        print(event)
        raise ValueError(f"Must use a specialised event. Given {event}")


def copy_file(event: CopyFile, uow: UnitOfWorkProtocol):
    with uow:
        uow.logger.info({"guid": uow.guid, "event": event})
        success = uow.repo.copy(event.src, event.dst)
        uow.logger.info({"guid": uow.guid, "success": success})


def move_file(event: MoveFile, uow: UnitOfWorkProtocol):
    with uow:
        uow.logger.info({"guid": uow.guid, "event": event})
        success = uow.repo.move(event.src, event.dst)
        uow.logger.info({"guid": uow.guid, "success": success})


def delete_file(event: DeleteFile, uow: UnitOfWorkProtocol):
    with uow:
        uow.logger.info({"guid": uow.guid, "event": event})
        success = uow.repo.delete(event.dst)
        uow.logger.info({"guid": uow.guid, "success": success})


EVENT_HANDLERS = {
    Event: example_handler,
    CopyFile: copy_file,
    MoveFile: move_file,
    DeleteFile: delete_file,
}
