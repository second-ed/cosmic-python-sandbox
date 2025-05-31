from cosmic_python_sandbox.service_layer.uow import UnitOfWorkProtocol
from cosmic_python_sandbox.usecases.events import (
    CopyFile,
    DeleteFile,
    Event,
    MoveFile,
)


def example_handler(event: Event, uow: UnitOfWorkProtocol) -> None:
    with uow:
        err_msg = f"Must use a specialised event. Given {event}"
        raise ValueError(err_msg)


def copy_file(event: CopyFile, uow: UnitOfWorkProtocol) -> None:
    with uow:
        uow.logger.info({"guid": uow.guid, "event": event})
        success = uow.repo.fs.copy(event.src, event.dst)
        uow.logger.info({"guid": uow.guid, "success": success})


def move_file(event: MoveFile, uow: UnitOfWorkProtocol) -> None:
    with uow:
        uow.logger.info({"guid": uow.guid, "event": event})
        success = uow.repo.fs.move(event.src, event.dst)
        uow.logger.info({"guid": uow.guid, "success": success})


def delete_file(event: DeleteFile, uow: UnitOfWorkProtocol) -> None:
    with uow:
        uow.logger.info({"guid": uow.guid, "event": event})
        success = uow.repo.fs.delete(event.dst)
        uow.logger.info({"guid": uow.guid, "success": success})
