from enum import Enum, auto
from typing import Protocol, TypeVar, runtime_checkable

import attrs

Data = TypeVar("Data")


class FileType(Enum):
    PARQUET = auto()
    CSV = auto()
    JSON = auto()


@runtime_checkable
class IOWrapperProtocol(Protocol):
    def setup(self) -> bool: ...

    def teardown(self) -> bool: ...

    def read(self, path: str, file_type: FileType) -> Data: ...

    def write(self, path: str, data: Data) -> bool: ...


@attrs.define
class FakeIOWrapper:
    db: dict = attrs.field()
    log: list = attrs.field(default=attrs.Factory(list))

    def setup(self) -> bool:
        return True

    def teardown(self) -> bool:
        return True

    def read(self, path: str, file_type: FileType) -> Data:
        self.log.append({"func": "read", "path": path, "file_type": file_type})
        return self.db.get(path)

    def write(self, path: str, data: Data) -> bool:
        self.log.append({"func": "write", "path": path})
        self.db[path] = data
        return True
