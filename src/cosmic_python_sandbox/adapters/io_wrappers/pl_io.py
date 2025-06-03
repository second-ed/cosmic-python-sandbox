import sqlite3

import attrs
import polars as pl

from cosmic_python_sandbox.adapters.io_wrappers._io_protocol import Data, FileType


@attrs.define
class PolarsIO:
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
                return pl.read_csv(path, **kwargs)
            case FileType.JSON:
                return pl.read_json(path, **kwargs)
            case FileType.PARQUET:
                return pl.read_parquet(path, **kwargs)
            case FileType.SQLITE3:
                return pl.read_database(query=path, connection=self.conn, **kwargs)
            case _:
                raise NotImplementedError(f"`{file_type}` is not implemented")
        return True

    def write(self, path: str, data: Data, file_type: FileType, **kwargs: dict) -> bool:
        match file_type:
            case FileType.CSV:
                data.write_csv(path, **kwargs)
            case FileType.JSON:
                data.write_json(path, **kwargs)
            case FileType.PARQUET:
                data.write_parquet(path, **kwargs)
            case FileType.SQLITE3:
                data.write_database(
                    table_name=path,
                    connection=self.conn,
                    **kwargs,
                )
            case _:
                raise NotImplementedError(f"`{file_type}` is not implemented")
        return True
