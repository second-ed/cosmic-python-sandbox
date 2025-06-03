import sqlite3

import attrs
import pandas as pd

from cosmic_python_sandbox.adapters.io_wrappers._io_protocol import Data, FileType


@attrs.define
class PandasIO:
    db_name: str = attrs.field(default="")
    conn: sqlite3.Connection | None = attrs.field(default=None)  # noqa: FA102

    def setup(self) -> bool:
        if self.db_name:
            self.conn = sqlite3.connect(self.db_name)
        return True

    def teardown(self) -> bool:
        if self.conn is not None:
            self.conn.close()
        return True

    def read(self, path: str, file_type: FileType, **kwargs: dict) -> Data:
        match file_type:
            case FileType.CSV:
                return pd.read_csv(path, **kwargs)
            case FileType.JSON:
                return pd.read_json(path, **kwargs)
            case FileType.PARQUET:
                return pd.read_parquet(path, **kwargs)
            case FileType.SQLITE3:
                return pd.read_sql(path, con=self.conn, **kwargs)
            case _:
                raise NotImplementedError(f"`{file_type}` is not implemented")
        return True

    def write(self, path: str, data: Data, file_type: FileType, **kwargs: dict) -> bool:
        match file_type:
            case FileType.CSV:
                data.to_csv(path, index=False, **kwargs)
            case FileType.JSON:
                data.to_json(path, index=False, orient="records", **kwargs)
            case FileType.PARQUET:
                data.to_parquet(path, index=False, **kwargs)
            case FileType.SQLITE3:
                data.to_sql(path, con=self.conn, **kwargs)
            case _:
                raise NotImplementedError(f"`{file_type}` is not implemented")
        return True
