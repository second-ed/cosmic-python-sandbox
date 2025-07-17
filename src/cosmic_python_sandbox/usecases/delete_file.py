import attrs
from attrs.validators import min_len

from cosmic_python_sandbox.service_layer.uow import UnitOfWorkProtocol
from cosmic_python_sandbox.usecases._event import Event, catch_err


@attrs.define
class DeleteFile(Event):
    dst: str = attrs.field(default="", validator=[min_len(3)])


@catch_err
def delete_file(event: DeleteFile, uow: UnitOfWorkProtocol) -> None:
    with uow:
        uow.logger.info({"guid": uow.guid, "event": event})
        success = uow.repo.fs.delete(event.dst)
        uow.logger.info({"guid": uow.guid, "success": success})
