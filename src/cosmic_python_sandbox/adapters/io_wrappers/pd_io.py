import attrs
import pandas as pd

from cosmic_python_sandbox.adapters.io_wrappers._io_protocol import Data, FileType


@attrs.define
class PandasIO:
    def setup(self) -> bool:
        return True

    def teardown(self) -> bool:
        return True

    def read(self, path: str, file_type: FileType, **kwargs: dict) -> Data:
        match file_type:
            case FileType.CSV:
                return pd.read_csv(path, **kwargs)
            case FileType.JSON:
                return pd.read_json(path, **kwargs)
            case FileType.PARQUET:
                return pd.read_parquet(path, **kwargs)
        return True

    def write(self, path: str, data: Data, file_type: FileType, **kwargs: dict) -> bool:
        match file_type:
            case FileType.CSV:
                data.to_csv(path, index=False, **kwargs)
            case FileType.JSON:
                data.to_json(path, index=False, orient="records", **kwargs)
            case FileType.PARQUET:
                data.to_parquet(path, index=False, **kwargs)
        return True
