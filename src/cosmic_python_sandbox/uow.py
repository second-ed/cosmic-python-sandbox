import uuid
from typing import Callable, Protocol, runtime_checkable

import attrs

from cosmic_python_sandbox.io_mod import IOWrapperProtocol
from cosmic_python_sandbox.logger import LoggerProtocol


@runtime_checkable
class UnitOfWorkProtocol(Protocol):
    def __enter__(self): ...

    def __exit__(self, exc_type, exc_val, exc_tb): ...


@attrs.define
class UnitOfWork(UnitOfWorkProtocol):
    repo: IOWrapperProtocol = attrs.field()
    logger: LoggerProtocol = attrs.field()
    guid_generator: Callable = attrs.field(default=uuid.uuid4)
    guid: str = attrs.field(default="")

    def __enter__(self):
        self.guid = str(self.guid_generator())
        self.logger.info({"guid": self.guid, "msg": "Initialising UOW"})

        # generic setup ops
        self.repo.setup()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.logger.error({"guid": self.guid, "msg": exc_val})
        else:
            self.logger.info({"guid": self.guid, "msg": "Completed UOW"})

        # clean up afterwards
        self.repo.teardown()
