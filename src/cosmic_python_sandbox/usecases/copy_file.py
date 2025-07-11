import attrs
from attrs.validators import min_len

from cosmic_python_sandbox.service_layer.uow import UnitOfWorkProtocol
from cosmic_python_sandbox.usecases._event import Event


@attrs.define
class CopyFile(Event):
    src: str = attrs.field(default="", validator=[min_len(3)])
    dst: str = attrs.field(default="", validator=[min_len(3)])


def copy_file(event: CopyFile, uow: UnitOfWorkProtocol) -> None:
    with uow:
        uow.logger.info({"guid": uow.guid, "event": event})
        success = uow.repo.fs.copy(event.src, event.dst)
        uow.logger.info({"guid": uow.guid, "success": success})
