from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Protocol, runtime_checkable

import attrs

if TYPE_CHECKING:
    from collections.abc import Callable
    from types import TracebackType

    from cosmic_python_sandbox.adapters.io_mod import IOWrapperProtocol
    from cosmic_python_sandbox.adapters.logger import LoggerProtocol


@runtime_checkable
class UnitOfWorkProtocol(Protocol):
    def __enter__(self) -> None: ...

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None: ...


@attrs.define
class UnitOfWork(UnitOfWorkProtocol):
    repo: IOWrapperProtocol = attrs.field()
    logger: LoggerProtocol = attrs.field()
    guid_generator: Callable = attrs.field(default=uuid.uuid4)
    guid: str = attrs.field(default="")

    def __enter__(self) -> None:
        self.guid = str(self.guid_generator())
        self.logger.info({"guid": self.guid, "msg": "Initialising UOW"})

        # generic setup ops
        self.repo.setup()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        if exc_type is not None:
            self.logger.error({"guid": self.guid, "msg": exc_val})
        else:
            self.logger.info({"guid": self.guid, "msg": "Completed UOW"})

        # clean up afterwards
        self.repo.teardown()
