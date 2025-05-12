import uuid
from enum import Enum, auto
from typing import Callable, Protocol, TypeVar, runtime_checkable

import attrs

from cosmic_python_sandbox.fake_logger import LoggerProtocol

Data = TypeVar("Data")


class FileType(Enum):
    PARQUET = auto()
    CSV = auto()
    JSON = auto()


@runtime_checkable
class IOWrapperProtocol(Protocol):
    def read(self, path: str, file_type: FileType) -> Data: ...

    def write(self, path: str, data: Data) -> bool: ...


@runtime_checkable
class UnitOfWorkProtocol(Protocol):
    def __enter__(self): ...

    def __exit__(self, exc_type, exc_val, exc_tb): ...


@attrs.define
class UnitOfWork:
    repo: IOWrapperProtocol = attrs.field()
    logger: LoggerProtocol = attrs.field()
    guid_generator: Callable = attrs.field(default=uuid.uuid4)
    guid: str = attrs.field(default="")

    def __enter__(self):
        self.guid = str(self.guid_generator())
        self.logger.info({"guid": self.guid, "msg": "Initialising UOW"})
        # any initialisation
        # self.repo.etc()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.logger.error({"guid": self.guid, "msg": exc_val})
        else:
            self.logger.info({"guid": self.guid, "msg": "Completed UOW"})
        # close connection to repo
        # self.repo.etc()
