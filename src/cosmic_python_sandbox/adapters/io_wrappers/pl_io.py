import attrs
import polars as pl

from cosmic_python_sandbox.adapters.io_wrappers._io_protocol import Data, FileType


@attrs.define
class PolarsIO:
    def setup(self) -> bool:
        return True

    def teardown(self) -> bool:
        return True

    def read(self, path: str, file_type: FileType, **kwargs: dict) -> Data:
        match file_type:
            case FileType.CSV:
                return pl.read_csv(path, **kwargs)
            case FileType.JSON:
                return pl.read_json(path, **kwargs)
            case FileType.PARQUET:
                return pl.read_parquet(path, **kwargs)
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
            case _:
                raise NotImplementedError(f"`{file_type}` is not implemented")
        return True
