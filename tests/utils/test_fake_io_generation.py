from pathlib import Path

import pytest

from cosmic_python_sandbox.utils.fake_io_generation import generate_fake_io, read_str

REPO_ROOT = Path(__file__).parents[2]


@pytest.mark.parametrize(
    "kwargs, expected_result_path",
    (
        (
            {
                "db_exts": ["parquet"],
                "external_exts": ["query_api"],
                "hash_types": ["md5"],
            },
            REPO_ROOT.joinpath("mock_data", "simple_fake_io.py"),
        ),
    ),
)
def test_generate_fake_io(kwargs, expected_result_path):
    assert generate_fake_io(**kwargs) == read_str(expected_result_path)
