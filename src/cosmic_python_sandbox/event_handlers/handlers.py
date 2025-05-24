from collections.abc import Callable, Sequence

from cosmic_python_sandbox.event_handlers.events import (
    CopyFile,
    DeleteFile,
    Event,
    MoveFile,
)
from cosmic_python_sandbox.service_layer.uow import UnitOfWorkProtocol

EventHandlers = dict[type, Callable[[Event], Event | Sequence[Event] | None]]


def example_handler(event: Event, uow: UnitOfWorkProtocol) -> None:
    with uow:
        err_msg = f"Must use a specialised event. Given {event}"
        raise ValueError(err_msg)


def copy_file(event: CopyFile, uow: UnitOfWorkProtocol) -> None:
    with uow:
        uow.logger.info({"guid": uow.guid, "event": event})
        success = uow.repo.copy(event.src, event.dst)
        uow.logger.info({"guid": uow.guid, "success": success})


def move_file(event: MoveFile, uow: UnitOfWorkProtocol) -> None:
    with uow:
        uow.logger.info({"guid": uow.guid, "event": event})
        success = uow.repo.move(event.src, event.dst)
        uow.logger.info({"guid": uow.guid, "success": success})


def delete_file(event: DeleteFile, uow: UnitOfWorkProtocol) -> None:
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
