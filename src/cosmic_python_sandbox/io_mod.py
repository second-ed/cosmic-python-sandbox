from copy import deepcopy
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

    def read(self, path: str, file_type: FileType) -> Data: ...

    def write(self, path: str, data: Data) -> bool: ...

    def teardown(self) -> bool: ...


@attrs.define
class FakeIO(IOWrapperProtocol):
    db: dict = attrs.field(default=attrs.Factory(dict))

    def setup(self) -> bool:
        return True

    def read(self, path: str, file_type: FileType) -> Data:
        return self.db[path]

    def write(self, path: str, data: Data) -> bool:
        self.db[path] = data
        return True

    def teardown(self) -> bool:
        return True

    def copy(self, path: str, new_path: str) -> bool:
        data = deepcopy(self.db[path])
        self.db[new_path] = data
        return True

    def move(self, path: str, new_path: str) -> bool:
        data = deepcopy(self.db[path])
        self.db[new_path] = data
        self.db.pop(path)
        return True

    def delete(self, path: str) -> bool:
        self.db.pop(path)
        return True
