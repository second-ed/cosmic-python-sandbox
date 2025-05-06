"""Example FakeIO class that covers most operations.
Fakes an editable db and external source that is read-only."""

import hashlib
import os
from copy import deepcopy
from typing import TypeVar

Data = TypeVar("Data")


class FakeIO:
    def __init__(self, db: dict = None, external_src: dict = None, strict: bool = True):
        self.db = db or {}
        self.external_src = external_src or {}
        self.log = []
        self.strict = strict

    def reset_db(self):
        self.db = {}

    def _check_db(self, path: str, ext: str) -> None:
        if path not in self.db:
            raise FileNotFoundError(f"{path = } not in {list(self.db.keys()) = }")

        if not self.strict:
            return

        path_ext = os.path.splitext(path)[-1]
        if path_ext != "":
            if not path_ext.endswith(ext):
                raise ValueError(f"Path does not have expected ext: {path = } {ext = }")

    def _read_db(self, path: str, ext: str, **kwargs) -> Data:
        self.log.append(("read", path, kwargs))
        self._check_db(path, ext)
        return self.db[path]

    def _write_db(self, data: Data, path: str, **kwargs) -> bool:
        self.log.append(("write", path, kwargs))
        self.db[path] = data
        return True

    def copy(self, path: str, new_path: str) -> bool:
        self.log.append(("copy", path, new_path))
        data = deepcopy(self.db[path])
        self.db[new_path] = data
        return True

    def move(self, path: str, new_path: str) -> bool:
        self.log.append(("move", path, new_path))
        data = deepcopy(self.db[path])
        self.db[new_path] = data
        self.db.pop(path)
        return True

    def remove(self, path: str) -> bool:
        self.log.append(("remove", path))
        self.db.pop(path)
        return True

    def is_file(self, path: str) -> bool:
        self.log.append(("is_file", path))
        return path in self.db

    def list_files(self, prefix: str = "") -> list[str]:
        self.log.append(("list_files", prefix))
        return [p for p in self.db if p.startswith(prefix)]

    def get_size(self, path: str) -> int:
        self.log.append(("get_size", path))
        return len(path.encode("utf-8"))

    def get_md5(self, path: str) -> str:
        self.log.append(("get_md5", path))
        return hashlib.md5(path.encode()).hexdigest()

    def read_parquet(self, path: str, **kwargs) -> Data:
        return self._read_db(path, "parquet", **kwargs)

    def write_parquet(self, data: Data, path: str, **kwargs) -> bool:
        return self._write_db(data, path, **kwargs)

    def _read_external_src(self, path: str, **kwargs) -> Data:
        self.log.append(("external_read", path, kwargs))
        return self.external_src[path]

    def query_api(self, path: str, **kwargs) -> Data:
        return self._read_external_src(path, **kwargs)
